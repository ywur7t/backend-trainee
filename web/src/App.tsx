import { useEffect, useMemo, useState } from "react";
import {
  createOrder,
  getOrder,
  getRestaurantMenu,
  getRestaurants,
  type MenuItem,
  type Order,
  type Restaurant,
} from "./api";
import "./styles.css";

const CUSTOMER_ID = 2;
const ADDRESS_ID = 2;
const DELIVERY_TYPE_ID = 3;

type CartItem = MenuItem & { quantity: number };

const money = (v: number | string) =>
  `${Number(v).toLocaleString("ru-RU")} ₽`;

function icon(name: string) {
  const n = name.toLowerCase();
  if (n.includes("суш") || n.includes("ролл")) return "🍣";
  if (n.includes("бургер")) return "🍔";
  if (n.includes("пиц")) return "🍕";
  if (n.includes("паст")) return "🍝";
  if (n.includes("салат")) return "🥗";
  if (n.includes("карто")) return "🍟";
  if (n.includes("cola") || n.includes("кол")) return "🥤";
  if (n.includes("коф")) return "☕";
  return "🍽️";
}

function statusName(status: Order["status"]) {
  return typeof status === "object" ? status.name : status;
}

export default function App() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [restaurant, setRestaurant] = useState<Restaurant | null>(null);
  const [menu, setMenu] = useState<Awaited<ReturnType<typeof getRestaurantMenu>> | null>(null);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [category, setCategory] = useState<number | null>(null);
  const [order, setOrder] = useState<Order | null>(null);
  const [cartOpen, setCartOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");

  const count = useMemo(() => cart.reduce((s, x) => s + x.quantity, 0), [cart]);
  const total = useMemo(
    () => cart.reduce((s, x) => s + Number(x.price) * x.quantity, 0),
    [cart],
  );

  const items = useMemo(
    () =>
      menu?.items.filter(
        (x) => x.is_available && (category === null || x.category_id === category),
      ) ?? [],
    [menu, category],
  );

  useEffect(() => {
    getRestaurants()
      .then(setRestaurants)
      .catch((e) => setError(e instanceof Error ? e.message : "Ошибка загрузки"))
      .finally(() => setLoading(false));
  }, []);

  async function openRestaurant(r: Restaurant) {
    try {
      setWorking(true);
      setError("");
      const data = await getRestaurantMenu(r.id);
      setRestaurant(r);
      setMenu(data);
      setCategory(null);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Не удалось загрузить меню");
    } finally {
      setWorking(false);
    }
  }

  function change(id: number, delta: number) {
    setCart((current) =>
      current
        .map((x) => x.id === id ? { ...x, quantity: x.quantity + delta } : x)
        .filter((x) => x.quantity > 0),
    );
  }

  function add(item: MenuItem) {
    setCart((current) => {
      const existing = current.find((x) => x.id === item.id);
      return existing
        ? current.map((x) => x.id === item.id ? { ...x, quantity: x.quantity + 1 } : x)
        : [...current, { ...item, quantity: 1 }];
    });
  }

  async function submit() {
    if (!restaurant || !cart.length) return;
    try {
      setWorking(true);
      setError("");
      const created = await createOrder({
        customer_id: CUSTOMER_ID,
        restaurant_id: restaurant.id,
        address_id: ADDRESS_ID,
        delivery_type_id: DELIVERY_TYPE_ID,
        items: cart.map((x) => ({ menu_item_id: x.id, quantity: x.quantity })),
      });
      setOrder(created);
      setCart([]);
      setCartOpen(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка создания заказа");
    } finally {
      setWorking(false);
    }
  }

  async function refresh() {
    if (!order) return;
    try {
      setOrder(await getOrder(order.id));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка обновления");
    }
  }

  function home() {
    setRestaurant(null);
    setMenu(null);
    setOrder(null);
    setCategory(null);
    setCartOpen(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  if (loading) {
    return <div className="loading"><div className="spinner" />Загружаем рестораны</div>;
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <button className="logo" onClick={home}>
            <span className="logo-box">a</span>
            <span>авито<span className="light">.кухня</span></span>
          </button>
          <div className="header-right">
            <span className="customer">Клиент #{CUSTOMER_ID}</span>
            {count > 0 && !order && (
              <button className="cart-button" onClick={() => setCartOpen(true)}>
                Корзина <b>{count}</b><strong>{money(total)}</strong>
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="container">
        {error && (
          <div className="error">
            <span>{error}</span><button onClick={() => setError("")}>×</button>
          </div>
        )}

        {order ? (
          <section className="success">
            <div className="check">✓</div>
            <div className="eyebrow">ЗАКАЗ ПРИНЯТ</div>
            <h1>Заказ #{order.id}</h1>
            <p>Заказ успешно создан и передан ресторану.</p>
            <div className="summary">
              <div><span>Статус</span><strong className="status">{statusName(order.status)}</strong></div>
              {order.restaurant && <div><span>Ресторан</span><strong>{order.restaurant.name}</strong></div>}
              {order.delivery_address && (
                <div>
                  <span>Доставка</span>
                  <strong>
                    {order.delivery_address.city}, {order.delivery_address.street},{" "}
                    дом {order.delivery_address.house}
                    {order.delivery_address.apartment && `, кв. ${order.delivery_address.apartment}`}
                  </strong>
                </div>
              )}
              <div className="summary-total"><span>Итого</span><strong>{money(order.total_price)}</strong></div>
            </div>
            <div className="success-actions">
              <button className="primary" onClick={refresh}>Обновить статус</button>
              <button className="secondary" onClick={home}>Вернуться к ресторанам</button>
            </div>
          </section>
        ) : restaurant && menu ? (
          <section>
            <button className="back" onClick={home}>← Все рестораны</button>
            <div className="menu-head">
              <div>
                <div className="eyebrow">МЕНЮ РЕСТОРАНА</div>
                <h1>{menu.restaurant_name}</h1>
                <p>Выберите блюда и добавьте их в корзину.</p>
              </div>
              {count > 0 && (
                <button className="menu-cart" onClick={() => setCartOpen(true)}>
                  {count} блюд · {money(total)}
                </button>
              )}
            </div>

            <div className="categories">
              <button className={category === null ? "active" : ""} onClick={() => setCategory(null)}>Все</button>
              {menu.categories.map((c) => (
                <button key={c.id} className={category === c.id ? "active" : ""} onClick={() => setCategory(c.id)}>
                  {c.name}
                </button>
              ))}
            </div>

            <div className="food-grid">
              {items.map((item) => {
                const inCart = cart.find((x) => x.id === item.id);
                return (
                  <article className="food-card" key={item.id}>
                    <div className="food-image">{icon(item.name)}</div>
                    <div className="food-content">
                      <h3>{item.name}</h3>
                      <p>{item.description || "Вкусное блюдо из меню"}</p>
                      <div className="food-bottom">
                        <strong>{money(item.price)}</strong>
                        {inCart ? (
                          <div className="quantity">
                            <button onClick={() => change(item.id, -1)}>−</button>
                            <b>{inCart.quantity}</b>
                            <button onClick={() => change(item.id, 1)}>+</button>
                          </div>
                        ) : (
                          <button className="add" onClick={() => add(item)}>Добавить</button>
                        )}
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
            {!items.length && <div className="empty">В этой категории нет доступных блюд.</div>}
          </section>
        ) : (
          <section>
            <div className="hero">
              <div>
                <div className="eyebrow">АВИТО.КУХНЯ</div>
                <h1>Хорошая еда.<br />Без лишних движений.</h1>
                <p>Выберите ресторан, соберите заказ и оформите доставку за пару минут.</p>
              </div>
              <div className="hero-art">🍜</div>
            </div>

            <div className="section-title">
              <div><div className="eyebrow">НА СЕГОДНЯ</div><h2>Рестораны</h2></div>
              <span>{restaurants.length} заведений</span>
            </div>

            <div className="restaurants">
              {restaurants.map((r) => (
                <button className="restaurant" key={r.id} onClick={() => openRestaurant(r)}>
                  <div className="restaurant-image">{icon(r.name)}</div>
                  <div className="restaurant-info">
                    <div className="restaurant-status"><i />{r.is_open === false ? "Закрыто" : "Открыто"}</div>
                    <h3>{r.name}</h3>
                    <p>{r.description || "Доставка вкусной еды"}</p>
                  </div>
                  <span className="arrow">↗</span>
                </button>
              ))}
            </div>
            {!restaurants.length && <div className="empty">Рестораны пока не найдены.</div>}
          </section>
        )}
      </main>

      {cartOpen && !order && (
        <>
          <button className="backdrop" onClick={() => setCartOpen(false)} aria-label="Закрыть" />
          <aside className="drawer">
            <div className="drawer-head">
              <div><div className="eyebrow">ВАШ ЗАКАЗ</div><h2>Корзина</h2></div>
              <button className="close" onClick={() => setCartOpen(false)}>×</button>
            </div>

            <div className="drawer-items">
              {cart.map((item) => (
                <div className="drawer-item" key={item.id}>
                  <div className="drawer-icon">{icon(item.name)}</div>
                  <div>
                    <strong>{item.name}</strong>
                    <small>{money(item.price)} за шт.</small>
                    <div className="quantity">
                      <button onClick={() => change(item.id, -1)}>−</button>
                      <b>{item.quantity}</b>
                      <button onClick={() => change(item.id, 1)}>+</button>
                    </div>
                  </div>
                  <strong>{money(Number(item.price) * item.quantity)}</strong>
                </div>
              ))}
            </div>

            <div className="drawer-bottom">
              <div className="drawer-total"><span>Итого</span><strong>{money(total)}</strong></div>
              <div className="delivery">
                <span>Доставка</span>
                <strong>Москва, Тверская, дом 10, квартира 25</strong>
                <small>Клиент #{CUSTOMER_ID} · адрес #{ADDRESS_ID}</small>
              </div>
              <button className="primary full" disabled={working} onClick={submit}>
                {working ? "Оформляем…" : `Оформить · ${money(total)}`}
              </button>
            </div>
          </aside>
        </>
      )}
    </div>
  );
}
