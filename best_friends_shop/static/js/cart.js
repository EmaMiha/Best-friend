document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".add-to-cart").forEach(button => {
        button.addEventListener("click", function (event) {
<<<<<<< HEAD
            event.preventDefault(); 
=======
            event.preventDefault(); // Sprečava standardni submit
>>>>>>> ffd282190605125713a0abd263964f8a0e8f48d9

            const productId = this.getAttribute("data-product-id");
            const quantityInput = document.getElementById(`quantity-${productId}`);
            const quantity = quantityInput ? parseInt(quantityInput.value) : 1;

            if (!productId || isNaN(quantity) || quantity <= 0) {
                console.error("Invalid product ID or quantity");
                return;
            }

<<<<<<< HEAD
=======
            // Onemogućavanje dugmeta dok traje zahtev (sprečava dupli klik)
>>>>>>> ffd282190605125713a0abd263964f8a0e8f48d9
            this.disabled = true;

            fetch(`/add-to-cart/${productId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({ quantity: quantity })
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    showToast("Product added to cart!", "success");
                }
                if (data.cart_count !== undefined) {
                    document.getElementById("cart-count").innerText = data.cart_count;
                }
            })
            .catch(error => console.error("Error:", error))
            .finally(() => {
<<<<<<< HEAD
                this.disabled = false; 
=======
                this.disabled = false; // Ponovno omogućavanje dugmeta nakon završetka zahteva
>>>>>>> ffd282190605125713a0abd263964f8a0e8f48d9
            });
        });
    });
});

<<<<<<< HEAD
=======
// ✅ Funkcija za CSRF token
>>>>>>> ffd282190605125713a0abd263964f8a0e8f48d9
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

<<<<<<< HEAD
=======
// ✅ Funkcija za prikaz Toast notifikacije
>>>>>>> ffd282190605125713a0abd263964f8a0e8f48d9
function showToast(message, type = "success") {
    const toastContainer = document.getElementById("toast-container");
    if (!toastContainer) {
        console.error("Toast container not found.");
        return;
    }

    const toast = document.createElement("div");
    toast.className = `toast align-items-center text-bg-${type} border-0 show`;
    toast.setAttribute("role", "alert");

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}
