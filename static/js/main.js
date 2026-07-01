function showJsMessage(message, type) {
    const messagesContainer = document.querySelector("#js-messages");
    const messageElement = document.createElement("div");
    messageElement.classList.add("flash-message", "flash-" + type);
    messageElement.textContent = message;
    messagesContainer.appendChild(messageElement);
    
    setTimeout(function () {
                messageElement.remove();
            }, 3000);
};

function updateCartBadge(cartCount) {
    const cartBadge = document.querySelector(".cart-badge");
    cartBadge.textContent = cartCount;
    cartBadge.classList.remove("hidden");
}

const cartForms = document.querySelectorAll('.add-to-cart-form');

cartForms.forEach(function (form){
    form.addEventListener('submit', function (event) {
        event.preventDefault();
        
        const formData = new FormData(form);
        const submitButton = form.querySelector("button[type='submit']");
        const originalButtonText = submitButton.textContent;
        
        submitButton.disabled = true;
        submitButton.textContent = "Добавляем...";
        
        fetch(form.action, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            if (data.success) {
                updateCartBadge(data.cart_count);
                showJsMessage(data.message, "success");
            } else {
                showJsMessage(data.message, "error");
            }
        })
        .catch(function (error) {
            showJsMessage("Не удалось добавить товар. Попробуйте ещё раз", "error");
        })
        .finally(function () {
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
        });
    });
});