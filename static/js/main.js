// Get CSRF token once
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// --- Helper function to display messages ---
function displayMessage(message, type = 'info', timeout = 100) { // Timeout set to 100ms
    const messageContainer = document.getElementById('js-message-container');
    if (!messageContainer) {
        console.error('Message container not found. Ensure an element with id="js-message-container" exists in your HTML.');
        alert(message);
        return;
    }

    // Immediately remove any previous alert elements in the container
    while (messageContainer.firstChild) {
        messageContainer.removeChild(messageContainer.firstChild);
    }

    const alertDiv = document.createElement('div');
    alertDiv.classList.add('alert', `alert-${type}`, 'alert-dismissible', 'show'); // Removed 'fade' class
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;

    messageContainer.appendChild(alertDiv);

    if (timeout > 0) {
        setTimeout(() => {
            if (document.body.contains(alertDiv)) {
                alertDiv.remove(); // Direct removal as no 'fade' animation
            }
        }, timeout);
    }
}

// --- Helper function to update cart count display ---
function updateCartCount(count) {
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        cartCountElement.textContent = count;
        // Show/hide the badge based on count
        if (count > 0) {
            cartCountElement.classList.remove('d-none');
        } else {
            cartCountElement.classList.add('d-none');
        }
    }
}


// --- Add to Cart Form Handling ---
document.querySelectorAll('.add-to-cart-form').forEach(form => {
    form.addEventListener('submit', async function(event) {
        event.preventDefault();

        try {
            const response = await fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new FormData(this)
            });

            const data = await response.json();

            if (response.ok) {
                if (data.success) {
                    displayMessage('Item added to cart successfully!', 'success');

                    // 1. Update Cart Count
                    if (data.cart_count !== undefined) {
                        updateCartCount(data.cart_count);
                    }

                    // 2. Change "Add to Cart" button to "Checkout"
                    const submitButton = this.querySelector('.add-to-cart-btn'); // 'this' refers to the submitted form
                    if (submitButton) {
                        // Create a new 'Checkout' link
                        const checkoutLink = document.createElement('a');
                        checkoutLink.href = '/cart/'; // URL for cart detail page
                        checkoutLink.className = 'btn btn-success'; // Change button styling
                        checkoutLink.textContent = 'Checkout';

                        // Replace the old button with the new link
                        submitButton.replaceWith(checkoutLink);
                    }
                } else {
                    let errorMessage = 'An error occurred while adding to cart. Please check the form.';
                    if (data.errors) {
                        errorMessage = Object.values(data.errors).flat().join('<br>');
                    }
                    displayMessage('Error adding to cart: ' + errorMessage, 'danger');
                }
            } else {
                const errorText = await response.text();
                console.error('Server response was not OK:', response.status, response.statusText, errorText);
                displayMessage('An error occurred while adding to cart. Please try again.', 'danger');
            }
        } catch (error) {
            console.error('Fetch error during cart add:', error);
            displayMessage('An error occurred while adding to cart. Please try again.', 'danger');
        }
    });
});


// --- Remove from Cart Form Handling ---
document.querySelectorAll('.cart-remove-form').forEach(form => {
    form.addEventListener('submit', async function(event) {
        event.preventDefault();

        const row = this.closest('tr[data-product-id]');

        try {
            const response = await fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new FormData(this)
            });

            const data = await response.json();

            if (response.ok) {
                if (data.success) {
                    if (row) {
                        row.remove();
                    }
                    document.getElementById('cart-total-price-display').innerText = `$${data.cart_total_price.toFixed(2)}`;

                    if (data.cart_total_items === 0) {
                        const cartItemsBody = document.getElementById('cart-items-body');
                        if (cartItemsBody) {
                             cartItemsBody.innerHTML = `
                                <tr>
                                    <td colspan="5">
                                        <div id="empty-cart-message" class="alert alert-info text-center" role="alert">
                                            Your shopping cart is empty.
                                            <p class="mt-2"><a href="{% url 'products:product_list' %}" class="alert-link">Start shopping now!</a></p>
                                        </div>
                                    </td>
                                </tr>`;
                            const table = document.querySelector('.table');
                            if (table) {
                                table.querySelector('thead').style.display = 'none';
                            }
                            const buttonsContainer = document.querySelector('.d-grid.gap-2.d-md-flex');
                            if (buttonsContainer) {
                                buttonsContainer.style.display = 'none';
                            }
                        }
                    }
                    displayMessage('Item removed from cart successfully!', 'success');

                    // Update Cart Count after removal
                    if (data.cart_count !== undefined) {
                        updateCartCount(data.cart_count);
                    }
                } else {
                    let errorMessage = 'An error occurred while removing item. Please try again.';
                    if (data.message) {
                        errorMessage = data.message;
                    }
                    displayMessage('Error removing item: ' + errorMessage, 'danger');
                }
            } else {
                const errorText = await response.text();
                console.error('Server response not OK:', response.status, response.statusText, errorText);
                displayMessage('An error occurred while removing item. Please try again.', 'danger');
            }
        } catch (error) {
            console.error('Fetch error during cart remove:', error);
            displayMessage('An error occurred while removing item. Please try again.', 'danger');
        }
    });
});


// ~/my_ecommerce_project/static/js/main.js

// Function to update the sticky checkout bar's state
function updateStickyCheckoutBar(cartCount) {
    console.log(`DEBUG: updateStickyCheckoutBar called with count: ${cartCount}`); // ADD THIS LINE
    const stickyCartCountSpan = document.getElementById('sticky-cart-count');
    const stickyCheckoutButton = document.getElementById('sticky-checkout-button');

    if (stickyCartCountSpan) {
        stickyCartCountSpan.textContent = cartCount;
    }

    if (stickyCheckoutButton) {
        if (cartCount > 0) {
            stickyCheckoutButton.classList.remove('disabled');
            stickyCheckoutButton.removeAttribute('aria-disabled');
            stickyCheckoutButton.setAttribute('tabindex', '0');
        } else {
            stickyCheckoutButton.classList.add('disabled');
            stickyCheckoutButton.setAttribute('aria-disabled', 'true');
            stickyCheckoutButton.setAttribute('tabindex', '-1');
        }
    }
}

// Initial update on page load when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DEBUG: DOMContentLoaded fired. Initializing sticky bar.'); // ADD THIS LINE
    const initialCartCountElement = document.getElementById('sticky-cart-count');
    if (initialCartCountElement) {
        const initialCartCount = parseInt(initialCartCountElement.textContent, 10);
        updateStickyCheckoutBar(initialCartCount);
    }

    // --- YOUR AJAX INTEGRATION STARTS HERE ---

    // For `cart_add` forms (e.g., on product detail page).
    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        console.log('DEBUG: Found add-to-cart-form. Attaching event listener.'); // ADD THIS LINE
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            console.log('DEBUG: Add to cart form submitted via AJAX.'); // ADD THIS LINE
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.elements.csrfmiddlewaretoken.value
                },
                body: new FormData(this)
            })
            .then(response => {
                console.log('DEBUG: Add to cart fetch response received:', response); // ADD THIS LINE
                return response.json();
            })
            .then(data => {
                console.log('DEBUG: Add to cart AJAX data:', data); // ADD THIS LINE
                if (data.success) {
                    console.log('DEBUG: Add to cart AJAX successful. Updating bars.'); // ADD THIS LINE
                    // Update HEADER cart count
                    const headerCartCountSpan = document.getElementById('cart-count');
                    if (headerCartCountSpan) {
                        headerCartCountSpan.textContent = data.cart_count;
                        headerCartCountSpan.classList.toggle('d-none', data.cart_count === 0);
                    }

                    // Update STICKY BOTTOM cart count
                    updateStickyCheckoutBar(data.cart_count);

                    console.log('Product added to cart!');

                } else {
                    console.error("Error adding to cart:", data.errors);
                }
            })
            .catch(error => console.error('Network error on add to cart:', error));
        });
    });

    // For `cart_remove` forms (e.g., on cart detail page).
    document.querySelectorAll('.cart-remove-form').forEach(form => {
        console.log('DEBUG: Found cart-remove-form. Attaching event listener.'); // ADD THIS LINE
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            console.log('DEBUG: Remove from cart form submitted via AJAX.'); // ADD THIS LINE
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.elements.csrfmiddlewaretoken.value
                }
            })
            .then(response => {
                console.log('DEBUG: Remove from cart fetch response received:', response); // ADD THIS LINE
                return response.json();
            })
            .then(data => {
                console.log('DEBUG: Remove from cart AJAX data:', data); // ADD THIS LINE
                if (data.success) {
                    console.log('DEBUG: Remove from cart AJAX successful. Updating bars.'); // ADD THIS LINE
                    // Update HEADER cart count
                    const headerCartCountSpan = document.getElementById('cart-count');
                    if (headerCartCountSpan) {
                        headerCartCountSpan.textContent = data.cart_count;
                        headerCartCountSpan.classList.toggle('d-none', data.cart_count === 0);
                    }

                    // Update STICKY BOTTOM cart count
                    updateStickyCheckoutBar(data.cart_count);

                    // --- UI updates specific to the cart detail page after removal ---
                    const rowToRemove = form.closest('tr');
                    if (rowToRemove) {
                        rowToRemove.remove(); // Remove the item's row from the table

                        const cartTotalPriceDisplay = document.getElementById('cart-total-price-display');
                        if (cartTotalPriceDisplay) {
                            cartTotalPriceDisplay.textContent = `$${data.cart_total_price.toFixed(2)}`;
                        }
                    }

                    if (data.cart_count === 0) {
                        const cartTable = document.querySelector('.table');
                        const emptyMessage = document.getElementById('empty-cart-message');
                        const cartActions = document.querySelector('.d-grid.gap-2.d-md-flex');

                        if (cartTable) cartTable.remove();
                        if (cartActions) cartActions.remove();
                        if (emptyMessage) emptyMessage.classList.remove('d-none');
                    }
                } else {
                    console.error("Error removing from cart:", data.errors);
                }
            })
            .catch(error => console.error('Network error on remove from cart:', error));
        });
    });
});