const productos = [
    {
        nombre: "Hamburguesa Clásica",
        precio: 4.50,
        descripcion: "Hamburguesa con carne, queso y vegetales frescos"
    },
    {
        nombre: "Pizza Personal",
        precio: 3.00,
        descripcion: "Pizza individual con queso y pepperoni"
    },
    {
        nombre: "Ensalada Mixta",
        precio: 2.75,
        descripcion: "Ensalada fresca con lechuga, tomate y zanahoria"
    }
];

const lista = document.getElementById("lista-productos");

function renderizarProductos() {
    lista.innerHTML = "";

    productos.forEach(producto => {
        const div = document.createElement("div");
        div.classList.add("producto");

        div.innerHTML = `
            <strong>${producto.nombre}</strong><br>
            Precio: $${producto.precio}<br>
            ${producto.descripcion}
        `;

        lista.appendChild(div);
    });
}

renderizarProductos();

document.getElementById("btnAgregar").addEventListener("click", () => {
    const nombre = document.getElementById("nombre").value;
    const precio = document.getElementById("precio").value;
    const descripcion = document.getElementById("descripcion").value;

    if (nombre && precio && descripcion) {
        productos.push({ nombre, precio, descripcion });
        renderizarProductos();

        document.getElementById("nombre").value = "";
        document.getElementById("precio").value = "";
        document.getElementById("descripcion").value = "";
    }
});
