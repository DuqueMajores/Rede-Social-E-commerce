const products = [
  { id: 1, name: "Camisa Slim", price: 99.9, img: "https://down-br.img.susercontent.com/file/f2748d7f84362750197cb2423e613214" },
  { id: 2, name: "Tênis Casual", price: 199.9, img: "https://down-br.img.susercontent.com/file/sg-11134201-7rbmy-lqni1byr0fwb4e" },
  { id: 3, name: "Calça Jeans", price: 149.9, img: "https://fernandaramosstore.com.br/wp-content/uploads/2024/11/fernandaramosstore_com_br-calca-jeans-feminina-cargo-natasha-lavagem-escura-199.jpeg" },
  { id: 4, name: "Camisa Slim", price: 99.9, img: "https://down-br.img.susercontent.com/file/f2748d7f84362750197cb2423e613214" }
];

const productsContainer = document.getElementById("products");
const cartItems = document.getElementById("cartItems");
const openCartBtn = document.getElementById("openCart");
const closeCartBtn = document.getElementById("closeCart");
const cart = document.getElementById("cart");

let cartData = [];

products.forEach((product) => {
  const card = document.createElement("div");
  card.classList.add("product");
  card.innerHTML = `
    <img src="${product.img}" alt="${product.name}" />
    <h3>${product.name}</h3>
    <p>R$ ${product.price.toFixed(2)}</p>
    <button onclick="addToCart(${product.id})">Adicionar ao Carrinho</button>
    <button class="message-btn" onclick="sendMessage(${product.id})">Menssagem</button>
    <button class="delete-btn" onclick="deleteProduct(${product.id}, this)">Excluir Produto</button>
  `;
  productsContainer.appendChild(card);
});

function addToCart(id) {
  const product = products.find(p => p.id === id);
  cartData.push(product);
  renderCart();
}

function sendMessage(id) {
  const product = products.find(p => p.id === id);
  alert(`Mensagem para o produto: ${product.name}`);
}

function deleteProduct(id, btnElement) {
  // Remove o produto do array 'products' se desejar (não recomendado pois altera a lista original)
  // Aqui vamos apenas remover o card do DOM para efeito visual:
  const card = btnElement.parentElement; // div .product
  productsContainer.removeChild(card);
  
  // Opcional: remover do carrinho caso esteja adicionado
  cartData = cartData.filter(item => item.id !== id);
  renderCart();
}

function renderCart() {
  cartItems.innerHTML = "";
  cartData.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = `${item.name} - R$ ${item.price.toFixed(2)}`;
    cartItems.appendChild(li);
  });
}

openCartBtn.addEventListener("click", () => cart.classList.add("open"));
closeCartBtn.addEventListener("click", () => cart.classList.remove("open"));
