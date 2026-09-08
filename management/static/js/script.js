/* =========================================================
   HOSPITAL MANAGEMENT SYSTEM
   Main JavaScript
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       PAGE LOAD ANIMATION
       ===================================================== */

    const mainContent = document.querySelector(".main-content");

    if (mainContent) {
        mainContent.classList.add("page-animation");
    }


    /* =====================================================
       AUTO HIDE ALERT MESSAGES
       ===================================================== */

    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(function (alert) {

        setTimeout(function () {

            alert.style.opacity = "0";
            alert.style.transform = "translateX(20px)";

            setTimeout(function () {
                alert.remove();
            }, 400);

        }, 4000);

    });


    /* =====================================================
       DELETE CONFIRMATION
       ===================================================== */

    const deleteButtons = document.querySelectorAll(
        ".delete-btn, .btn-danger"
    );

    deleteButtons.forEach(function (button) {

        button.addEventListener("click", function (event) {

            const confirmed = confirm(
                "Are you sure you want to delete this record?"
            );

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });


    /* =====================================================
       SEARCH / FILTER TABLE
       ===================================================== */

    const searchInputs = document.querySelectorAll(
        ".search-input, #searchInput"
    );

    searchInputs.forEach(function (searchInput) {

        searchInput.addEventListener("input", function () {

            const searchValue =
                searchInput.value.toLowerCase().trim();

            const table =
                searchInput.closest(".card")
                    ?.querySelector("table") ||
                document.querySelector("table");

            if (!table) {
                return;
            }

            const rows =
                table.querySelectorAll("tbody tr");

            rows.forEach(function (row) {

                const rowText =
                    row.textContent.toLowerCase();

                if (rowText.includes(searchValue)) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }

            });

        });

    });


    /* =====================================================
       FORM SUBMISSION LOADING EFFECT
       ===================================================== */

    const forms = document.querySelectorAll("form");

    forms.forEach(function (form) {

        form.addEventListener("submit", function () {

            const submitButton =
                form.querySelector(
                    "button[type='submit'], input[type='submit']"
                );

            if (submitButton) {

                submitButton.style.opacity = "0.75";
                submitButton.style.pointerEvents = "none";

                if (submitButton.tagName === "BUTTON") {

                    submitButton.dataset.originalText =
                        submitButton.innerHTML;

                    submitButton.innerHTML =
                        "Processing...";

                }

            }

        });

    });


    /* =====================================================
       PASSWORD SHOW / HIDE
       ===================================================== */

    const passwordToggles =
        document.querySelectorAll(".password-toggle");

    passwordToggles.forEach(function (toggle) {

        toggle.addEventListener("click", function () {

            const input =
                document.querySelector(
                    toggle.dataset.target
                );

            if (!input) {
                return;
            }

            if (input.type === "password") {

                input.type = "text";
                toggle.textContent = "🙈";

            } else {

                input.type = "password";
                toggle.textContent = "👁";

            }

        });

    });


    /* =====================================================
       PASSWORD VALIDATION
       ===================================================== */

    const passwordInputs =
        document.querySelectorAll(
            "input[name='password']"
        );

    passwordInputs.forEach(function (password) {

        password.addEventListener("input", function () {

            if (password.value.length < 6) {

                password.style.borderColor = "#ef4444";

            } else {

                password.style.borderColor = "#22c55e";

            }

        });

    });


    /* =====================================================
       CONFIRM PASSWORD
       ===================================================== */

    const confirmPasswordInputs =
        document.querySelectorAll(
            "input[name='confirm_password']"
        );

    confirmPasswordInputs.forEach(function (confirmPassword) {

        confirmPassword.addEventListener("input", function () {

            const form = confirmPassword.closest("form");

            if (!form) {
                return;
            }

            const password =
                form.querySelector(
                    "input[name='password']"
                );

            if (!password) {
                return;
            }

            if (
                confirmPassword.value !== "" &&
                confirmPassword.value === password.value
            ) {

                confirmPassword.style.borderColor =
                    "#22c55e";

            } else {

                confirmPassword.style.borderColor =
                    "#ef4444";

            }

        });

    });


    /* =====================================================
       INPUT FOCUS EFFECT
       ===================================================== */

    const inputs =
        document.querySelectorAll(
            "input, select, textarea"
        );

    inputs.forEach(function (input) {

        input.addEventListener("focus", function () {

            input.parentElement?.classList.add(
                "input-focused"
            );

        });

        input.addEventListener("blur", function () {

            input.parentElement?.classList.remove(
                "input-focused"
            );

        });

    });


    /* =====================================================
       BUTTON RIPPLE EFFECT
       ===================================================== */

    const buttons =
        document.querySelectorAll(
            "button, .btn"
        );

    buttons.forEach(function (button) {

        button.addEventListener("click", function (event) {

            const ripple =
                document.createElement("span");

            ripple.classList.add("ripple");

            const rect =
                button.getBoundingClientRect();

            ripple.style.left =
                (event.clientX - rect.left) + "px";

            ripple.style.top =
                (event.clientY - rect.top) + "px";

            button.appendChild(ripple);

            setTimeout(function () {
                ripple.remove();
            }, 600);

        });

    });


    /* =====================================================
       STAT NUMBER ANIMATION
       ===================================================== */

    const statNumbers =
        document.querySelectorAll(
            ".stat-card .number"
        );

    statNumbers.forEach(function (element) {

        const finalNumber =
            parseInt(
                element.textContent.replace(/\D/g, ""),
                10
            );

        if (isNaN(finalNumber)) {
            return;
        }

        let currentNumber = 0;

        const duration = 800;
        const steps = 30;
        const increment =
            finalNumber / steps;

        const interval =
            setInterval(function () {

                currentNumber += increment;

                if (currentNumber >= finalNumber) {

                    currentNumber = finalNumber;
                    clearInterval(interval);

                }

                element.textContent =
                    Math.floor(currentNumber);

            }, duration / steps);

    });


    /* =====================================================
       SIDEBAR ACTIVE LINK
       ===================================================== */

    const currentPath =
        window.location.pathname;

    const sidebarLinks =
        document.querySelectorAll(
            ".sidebar a"
        );

    sidebarLinks.forEach(function (link) {

        const linkPath =
            new URL(
                link.href,
                window.location.origin
            ).pathname;

        if (
            linkPath === currentPath &&
            currentPath !== "/"
        ) {

            link.classList.add("active");

        }

    });


    /* =====================================================
       TABLE ROW ANIMATION
       ===================================================== */

    const tableRows =
        document.querySelectorAll(
            "tbody tr"
        );

    tableRows.forEach(function (row, index) {

        row.style.opacity = "0";
        row.style.transform = "translateY(8px)";

        setTimeout(function () {

            row.style.transition =
                "opacity 0.35s ease, transform 0.35s ease";

            row.style.opacity = "1";
            row.style.transform = "translateY(0)";

        }, index * 40);

    });


    /* =====================================================
       TOOLTIP FOR BUTTONS
       ===================================================== */

    const tooltipElements =
        document.querySelectorAll(
            "[data-tooltip]"
        );

    tooltipElements.forEach(function (element) {

        element.addEventListener("mouseenter", function () {

            element.title =
                element.dataset.tooltip;

        });

    });


    /* =====================================================
       PREVENT DOUBLE CLICK FORM SUBMISSION
       ===================================================== */

    forms.forEach(function (form) {

        form.addEventListener("submit", function () {

            if (form.dataset.submitted === "true") {
                return;
            }

            form.dataset.submitted = "true";

        });

    });


    /* =====================================================
       CONSOLE MESSAGE
       ===================================================== */

    console.log(
        "Hospital Management System loaded successfully."
    );

});