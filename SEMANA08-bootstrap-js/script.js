function mostrarAlerta() {
    alert("Bienvenido a la página interactiva creada con Bootstrap y JavaScript");
}

document.getElementById("formContacto").addEventListener("submit", function(event) {
    event.preventDefault();

    let nombre = document.getElementById("nombre").value;
    let correo = document.getElementById("correo").value;
    let mensaje = document.getElementById("mensaje").value;

    let valido = true;

    document.getElementById("errorNombre").textContent = "";
    document.getElementById("errorCorreo").textContent = "";
    document.getElementById("errorMensaje").textContent = "";

    if (nombre === "") {
        document.getElementById("errorNombre").textContent = "El nombre es obligatorio";
        valido = false;
    }

    if (correo === "") {
        document.getElementById("errorCorreo").textContent = "El correo es obligatorio";
        valido = false;
    }

    if (mensaje === "") {
        document.getElementById("errorMensaje").textContent = "El mensaje es obligatorio";
        valido = false;
    }

    if (valido) {
        alert("Formulario enviado correctamente");
        document.getElementById("formContacto").reset();
    }
});
