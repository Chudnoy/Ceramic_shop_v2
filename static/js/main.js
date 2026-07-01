const cartForms = document.querySelectorAll('.add_to_cart_form');

cartForms.forEach(function (form){
    form.addEventListener('submit', function (event) {
        event.preventDefault();
        
        console.log('Форма добавления в корзину перехвачена');
    });
});