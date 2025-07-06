document.addEventListener("DOMContentLoaded", function () {
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
});
