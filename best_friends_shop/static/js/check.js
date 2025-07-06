document.addEventListener("DOMContentLoaded", function () {
<<<<<<< HEAD
  const applyBtn = document.getElementById("applyDiscount");
  const discountInput = document.getElementById("discountCode");
  const discountHidden = document.getElementById("discount_code_hidden");
  const discountedPrice = document.getElementById("discountedPrice");
  const total = parseFloat(document.getElementById("checkoutTotal").innerText);

  const codes = { "SAVE10": 10, "SAVE20": 20 };

  applyBtn.addEventListener("click", () => {
    const code = discountInput.value.trim().toUpperCase();
    if (codes[code]) {
      const percent = codes[code];
      const newTotal = total - (total * percent / 100);
      discountedPrice.innerText = newTotal.toFixed(2);
      discountHidden.value = code;
    } else {
      discountedPrice.innerText = total.toFixed(2);
      discountHidden.value = "";
      alert("Invalid discount code");
    }
  });
=======
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
>>>>>>> ffd282190605125713a0abd263964f8a0e8f48d9
});
