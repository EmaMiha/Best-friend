document.addEventListener("DOMContentLoaded", function () {
    let applyDiscountBtn = document.getElementById("applyDiscount");
    let discountInput = document.getElementById("discount_code");
    let originalPriceElement = document.getElementById("originalPrice");
    let discountMessage = document.getElementById("discount_message");
    let discountedPrice = document.getElementById("discountedPrice");

    applyDiscountBtn.addEventListener("click", function () {
        let discountCode = discountInput.value.trim();
        let totalPrice = parseFloat(originalPriceElement.getAttribute("data-total"));

        let validDiscounts = JSON.parse(localStorage.getItem("discount_codes")) || {};
        if (discountCode in validDiscounts) {
            let discountPercentage = validDiscounts[discountCode];
            let discountAmount = (totalPrice * discountPercentage) / 100;
            let newTotal = totalPrice - discountAmount;

            discountMessage.innerHTML = `✅ Discount applied! You saved ${discountPercentage}%.`;
            discountedPrice.innerHTML = `New Total: <strong>$${newTotal.toFixed(2)}</strong>`;
        } else {
            discountMessage.innerHTML = "❌ Invalid discount code.";
            discountedPrice.innerHTML = "";
        }
    });
});
