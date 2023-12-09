from gevent import monkey
monkey.patch_all()

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button 

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
from forms import UserForm, PairForm, RemoveDeviceForm
from flask_wtf import Form
from wtforms.validators import DataRequired
from sqlalchemy import func
from datetime import datetime
from flask_socketio import SocketIO
import bcrypt

import subprocess


app = Flask(__name__)
app.secret_key = 'splash'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")


db = SQLAlchemy(app)


login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'  

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first = db.Column(db.String)
    last = db.Column(db.String)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    deviceName = db.Column(db.String(400))
    deviceType = db.Column(db.String(300),unique=True)
    deviceStatus = db.Column(db.Integer)
    deviceLevel = db.Column(db.Integer)
    deviceBound = db.Column(db.Integer,nullable=True)
    
    def get_user(self, num):
        usr = User.query.filter_by(id = num).first()
        if not usr == None:
            return usr.username
        else:
            return 'Unknown user'


def __repr__(self):
    return f'<User {self.username}>'

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html', user=current_user)


@app.route('/home')
@login_required
def home():
    return render_template('home.html', user=current_user)



@app.route('/login', methods=['GET', 'POST'])
def login():
    errorMessage = ''
    if request.method == 'POST':
            # Authenticate the user and log them in
            user = User.query.filter_by(username=request.form['username']).first()
            if bcrypt.checkpw((request.form['password']).encode('utf-8'), user.password):
                login_user(user)
                
                return redirect(url_for('home'))
            else:
                errorMessage ='Login failed. Check your credentials.'
    return render_template('login.html', error=errorMessage)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return render_template('login.html')

@app.route('/viewdevices', methods=['POST','GET'])
@login_required
def devices():

    all_devices = Device.query.all()
    devices = []
    for i in all_devices:
        devDetails = {}
        devDetails['id'] = i.id
        devDetails['devType'] = i.deviceType
        devDetails['devName'] = i.deviceName
        devDetails['devLevel'] = i.deviceLevel
        devDetails['devStatus'] = i.deviceStatus
        devDetails['devBound'] = i.deviceBound


        devices.append(devDetails)
        removeDevButton = RemoveDeviceForm(prefix = str(i.id))
        devDetails['devRemoveDevButton'] = removeDevButton


    for i in devices:
        if i['devRemoveDevButton'].validate_on_submit():
            removeDevice = Device.query.filter_by(id = i['id'])
            for k in removeDevice:
                db.session.delete(k)
                db.session.commit()
                
                return redirect('/viewdevices')
        


    return render_template('devices.html', devices = devices)


@app.route('/pairdevice',methods = ['POST','GET'])
@login_required
def pairDevice():
    current_form = PairForm()
    if current_form.validate_on_submit():
        dev = Device()
        dev.id = current_form.deviceID.data
        dev.deviceType = current_form.deviceType.data
        dev.deviceName = current_form.deviceName.data
        dev.deviceStatus = False
        dev.deviceLevel = 127
        if (dev.deviceType == 'MatterSwitch'):
            dev.deviceBound = False

        command =  (
            "./chip-tool-debug pairing ble-thread "
            f"{dev.id} hex:0e08000000000001000035060004001fffe00708fd2699b601823ca10c0402a0f7f8051000112233445566778899aabbccddeeff030e4f70656e54687265616444656d6f0410445f2b5ca6f2a93a55ce570a70efeecb000300000f0208111111112222222201021234"
            " 20202021 3840"
        )
        try:
            subprocess.run(command, shell=True, check=True)
            with app.app_context():
                exist_rec = Device.query.filter_by(deviceType=dev.deviceType).first()
                if exist_rec:
                    exist_rec.id = dev.id
                    exist_rec.deviceName = dev.deviceName
                else:
                    db.session.add(dev)
                    db.session.commit()
            return redirect('/viewdevices')
        except subprocess.CalledProcessError:
            return jsonify({"status": "Failed to execute command"}), 500        

    return render_template('pair.html', form=current_form)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
   
    userDetails = {}
    userDetails['Username'] = current_user.username
    userDetails['UserEmail'] = current_user.email
    userArray = []
    userArray.append(userDetails)


    return render_template('settings.html',userArray=userArray)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    print('Hello')
    errorMessage = ' '
    cform = UserForm()

    if cform.validate_on_submit():
        # Process the form data, create a new user account, and check the registration
        user = User()
        user.username = cform.username.data
        user.email = cform.email.data
        user.password = bcrypt.hashpw((cform.password.data).encode('utf-8'), bcrypt.gensalt())
        print('User hashed Password is:', user.password)
        print('Adding user')
        db.session.add(user)
        try:
            db.session.commit()    
            print('Successful')
            flash('Signup successful! You are now registered.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Check your input.', 'error')
    return render_template('signup.html',form=cform, error=errorMessage)

@app.route('/delete_account',methods=['GET', 'POST'])
@login_required
def delete_account():
    current_form = Delete_Account_Form()
    user = User.query.filter_by(username=current_user.username).first()
    if current_form.validate_on_submit() and check_password_hash(user.password,current_form.password.data):
        db.session.delete(user) #deleting user
        db.session.commit()
        return redirect('/signup')
    return render_template('delete_account.html', form = current_form)

@app.route('/users')
def users():
    all_users = User.query.all()
    return render_template('users.html',users=all_users)

@app.route('/ClearCache',methods=['POST'])
@login_required
def Clear():
    command = "/bin/rm -rf /tmp/chip_*"
    subprocess.run(command, shell=True, check=True)
    return redirect(url_for('devices')) 

    
    
@app.route('/bindevice/<int:device_id>', methods=['POST'])
@login_required
def Bind_device(device_id):    
    light = Device.query.filter_by(deviceType="MatterLight").first()
    if light is None:
        flash('You must add a MatterLight device first', 'Failed')
        return redirect(url_for('devices'))
    else:
        command1 = (
            f"./chip-tool-debug accesscontrol write acl '[{{\"fabricIndex\": 1, \"privilege\": 5, \"authMode\": 2, \"subjects\": [112233], \"targets\": null}}, "
            f"{{\"fabricIndex\": 1, \"privilege\": 3, \"authMode\": 2, \"subjects\": [{device_id}], \"targets\": [{{\"cluster\": 6, \"endpoint\": 1, \"deviceType\": null}}, "
            f"{{\"cluster\": 8, \"endpoint\": 1, \"deviceType\": null}}]}}]' {light.id} 0"
        )

        command2 = (
            f"./chip-tool-debug binding write binding '[{{\"fabricIndex\": 1, \"node\": {light.id}, \"endpoint\": 1, \"cluster\": 6}}, "
            f"{{\"fabricIndex\": 1, \"node\": {light.id}, \"endpoint\": 1, \"cluster\": 8}}]' {device_id} 1"
        )

        try:
            subprocess.run(command1, shell=True, check=True)
        except subprocess.CalledProcessError:
            return jsonify({"status": "Failed to execute command"}), 500


        try:
            subprocess.run(command2, shell=True, check=True)
        except subprocess.CalledProcessError:
            return jsonify({"status": "Failed to execute command"}), 500
        
        switch = Device.query.filter_by(id=device_id).first()
        switch.deviceBound = True
        print("Bound state is: ", switch.deviceBound)
        # device.deviceStatus = not device.deviceStatus
        db.session.commit()
        return redirect(url_for('devices'))

@socketio.on('changeLevel')
def Handle_Level_Change(data):
    device_id = data['device_id']
    brightness = data['brightness']

    device = Device.query.filter_by(id=device_id).first()
    command = f"./chip-tool-debug levelcontrol move-to-level {brightness} 1 0 0 {device_id} 1"
    try:
        subprocess.run(command, shell=True, check=True)
        device.deviceLevel = brightness
    except subprocess.CalledProcessError:
        pass
    db.session.commit()
    socketio.emit('Updated_Level', {'device_id': device_id, "brightness": brightness})



@socketio.on('toggleState')
def Toggle_Change_State(data):
    device_id = data['device_id']
    device = Device.query.filter_by(id=device_id).first()
    command = f"./chip-tool-debug onoff toggle {device_id} 1"
    try:
        subprocess.run(command, shell=True, check=True)
        device.deviceStatus = not device.deviceStatus
    except subprocess.CalledProcessError:
        pass

    db.session.commit()
    socketio.emit('Updated_Status', {'device_id': device_id, "device_status": device.deviceStatus})


@socketio.on('StateOn')
def Turn_device_On(data):
    device_id = data['device_id']
    light = Device.query.filter_by(deviceType="MatterLight").first()
    switch = Device.query.filter_by(id=device_id).first()
    command = f"./chip-tool-debug onoff on {light.id} 1"
    try:
        subprocess.run(command, shell=True, check=True)
        light.deviceStatus = True
        switch.deviceStatus = True
    except subprocess.CalledProcessError:
        pass

    db.session.commit()
    socketio.emit('Updated_Status', {'device_id': light.id, "device_status": light.deviceStatus})
    socketio.emit('Updated_Status', {'device_id': switch.id, "device_status": switch.deviceStatus})


@socketio.on('StateOff')
def Turn_device_On(data):
    device_id = data['device_id']
    light = Device.query.filter_by(deviceType="MatterLight").first()
    switch = Device.query.filter_by(id=device_id).first()
    command = f"./chip-tool-debug onoff off {light.id} 1"
    try:
        subprocess.run(command, shell=True, check=True)
        light.deviceStatus = False
        switch.deviceStatus = False
    except subprocess.CalledProcessError:
        pass


    db.session.commit()
    socketio.emit('Updated_Status', {'device_id': light.id, "device_status": light.deviceStatus})
    socketio.emit('Updated_Status', {'device_id': switch.id, "device_status": switch.deviceStatus})


@socketio.on('connect')
def start_connect():
    print('client connected')

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))



if __name__ == '__main__':
    app.run()
