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
};

function updateCartTotal(total) {
	const cartTotal = document.querySelector('.cart-total');

	if (cartTotal) {
		cartTotal.textContent = 'Итого ' + total + ' рублей';
	};
};

function showEmptyCart() {
	const cartContent = document.querySelector('.cart-content');

	if (cartContent) {
		cartContent.innerHTML = `
			<div class="empty-cart">
				<p>Корзина пуста</p>
				<a href="/catalog" class="btn btn-primary">Вернуться в каталог</a>
			</div>
		`;
	};
};

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


const removeCartForms = document.querySelectorAll('.remove-from-cart-form');

removeCartForms.forEach(function (form) {
	form.addEventListener('submit', function (event) {
		event.preventDefault();

		const submitButton = form.querySelector("button[type='submit']");
		const originalButtonText = submitButton.textContent;

		submitButton.disabled = true;
		submitButton.textContent = 'Удаляем...';

		fetch(form.action, {
			method: 'POST',
			headers: {
				'X-Requested-With': 'XMLHttpRequest'
			}
		})
		.then(function (response) {
			return response.json();
		})
		.then(function (data) {
			if (data.success) {
				const cartRow = form.closest('tr');

				updateCartBadge(data.cart_count);
				updateCartTotal(data.total);
				cartRow.remove()
				if (data.cart_count === 0) {
					showEmptyCart()
				}
				showJsMessage(data.message, 'success');
			} else {
				showJsMessage(data.message, 'error');
			}
		})
		.catch(function () {
			showJsMessage('Не удалось удалить товар. Попробуйте ещё раз', 'error');
		})
		.finally(function () {
			submitButton.disabled = false;
			submitButton.textContent = originalButtonText;
		});
	});
});