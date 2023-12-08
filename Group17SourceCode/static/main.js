// show and hide functions
const functions = document.querySelectorAll('.functions');

functions.forEach(functions => {
    functions.addEventListener('click', () => {
        functions.classList.toggle('open');

        // change icon after being clicked
        const icon = functions.querySelector('.functions__icon i');
        if (icon.className === 'uil uil-plus-circle') {
            icon.className = 'uil uil-minus-circle';
        } else {
            icon.className = 'uil uil-plus-circle';
        }
    })
})
