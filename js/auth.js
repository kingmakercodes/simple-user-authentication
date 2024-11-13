document.addEventListener('DOMContentLoaded', () =>{
    const loginForm= document.getElementById('login-form')
    const signupForm= document.getElementById('signup-form')
    const switchToLogin= document.getElementById('switch-to-login')
    const switchToSignup= document.getElementById('switch-to-signup')

    // switch to signup form
    switchToSignup.addEventListener('click', () => {
        loginForm.classList.add('hidden');
        signupForm.classList.remove('hidden');
    });

    // switch to log in form
    switchToLogin.addEventListener('click', () => {
        signupForm.classList.add('hidden');
        loginForm.classList.remove('hidden');
    })
})