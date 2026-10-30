/*
 * Everything a non-developer is likely to change lives here: prices, dishes,
 * cravings, contact numbers. Prices are in naira.
 *
 * Photos: put a photo in assets/img/ and set `img` to its path plus
 * `photo: true` (photos get a framed, rounded crop; illustrations are cut-outs).
 */
window.IYA = {
  currency: "₦",

  // International format without "+" or spaces, e.g. "2348012345678".
  // When set, the bag's checkout button sends the order on WhatsApp.
  whatsapp: "",
  // e.g. "+2348012345678". Used for "Call to order" when WhatsApp is empty.
  phone: "",
  // Optional form endpoint (Formspree, Mailchimp, etc.) for the email sign-up.
  signupEndpoint: "",

  // The weekly drop countdown: Friday (5) at 18:00 Lagos time.
  drop: { weekday: 5, hour: 18 },

  filters: [
    { id: "all", label: "Everything" },
    { id: "rice", label: "Rice" },
    { id: "swallow", label: "Swallow" },
    { id: "protein", label: "Protein" },
    { id: "sides", label: "Sides" },
    { id: "sweet", label: "Sweet & drinks" },
  ],

  cravings: [
    { label: "Starving", dish: "jollof-combo" },
    { label: "Spicy", dish: "fish-stew" },
    { label: "Swallow", dish: "amala-abula" },
    { label: "Sweet tooth", dish: "puff-puff" },
    { label: "Snacky", dish: "peppered-turkey" },
    { label: "Late night", dish: "fried-rice" },
  ],

  // heat / full / napkins are 0-5 ratings shown on the craving card.
  dishes: [
    {
      id: "jollof-combo", name: "Jollof Combo", cat: "rice", badge: "Bestseller", price: 5500,
      img: "assets/art/jollof-combo.svg",
      alt: "Plate of smoky party jollof with a peppered turkey wing and fried plantain",
      desc: "Smoky party jollof, a fat turkey wing and sweet dodo. The plate everybody orders.",
      heat: 3, full: 5, napkins: 3, serves: "Serves 1",
    },
    {
      id: "peppered-turkey", name: "Peppered Turkey", cat: "protein", badge: "Extra loud", price: 6000,
      img: "assets/art/peppered-turkey.svg",
      alt: "Three fried turkey wings tossed in pepper sauce",
      desc: "Seasoned overnight, fried till the edges crackle, then tossed in ata dindin.",
      heat: 4, full: 3, napkins: 5, serves: "3 wings",
    },
    {
      id: "fish-stew", name: "Titus Fish Stew", cat: "protein", badge: "Hot", price: 4500,
      img: "assets/art/fish-stew.svg",
      alt: "Mackerel steaks in a rich red pepper stew",
      desc: "Mackerel steaks swimming in rich tomato-pepper stew. Perfect with white rice or yam.",
      heat: 5, full: 3, napkins: 4, serves: "Serves 1",
    },
    {
      id: "dodo", name: "Sweet Dodo", cat: "sides", badge: "Side", price: 1200,
      img: "assets/art/dodo.svg",
      alt: "Plate of golden fried plantain slices",
      desc: "Ripe plantain fried golden at the edges, soft and sweet in the middle.",
      heat: 0, full: 2, napkins: 2, serves: "Side",
    },
    {
      id: "amala-abula", name: "Amala Abula", cat: "swallow", badge: "Mama's fave", price: 3500,
      img: "assets/art/amala-abula.svg",
      alt: "Amala with ewedu, gbegiri and stew with meat",
      desc: "Soft amala with ewedu and gbegiri, finished with a ladle of stew and assorted meat.",
      heat: 3, full: 5, napkins: 2, serves: "Serves 1",
    },
    {
      id: "yam-egusi", name: "Pounded Yam & Egusi", cat: "swallow", badge: "", price: 4500,
      img: "assets/art/yam-egusi.svg",
      alt: "Pounded yam with egusi soup, ugu leaves and meat",
      desc: "Smooth pounded yam with egusi loaded with ugu leaves and assorted meat.",
      heat: 2, full: 5, napkins: 2, serves: "Serves 1",
    },
    {
      id: "fried-rice", name: "Fried Rice & Chicken", cat: "rice", badge: "Late night", price: 5000,
      img: "assets/art/fried-rice.svg",
      alt: "Vegetable fried rice with a fried chicken drumstick and plantain",
      desc: "Veggie fried rice with crispy fried chicken and two slices of dodo.",
      heat: 1, full: 4, napkins: 3, serves: "Serves 1",
    },
    {
      id: "moi-moi", name: "Moi Moi", cat: "sides", badge: "", price: 1000,
      img: "assets/art/moi-moi.svg",
      alt: "Steamed bean pudding with boiled egg on a leaf",
      desc: "Steamed bean pudding with egg. Soft, peppery and properly filling.",
      heat: 2, full: 3, napkins: 1, serves: "Side",
    },
    {
      id: "puff-puff", name: "Puff-Puff", cat: "sweet", badge: "Sweet", price: 800,
      img: "assets/art/puff-puff.svg",
      alt: "Pile of sugar-dusted puff-puff",
      desc: "Ten fluffy, sugar-dusted puff-puff, hot from the oil.",
      heat: 0, full: 2, napkins: 3, serves: "10 pieces",
    },
    {
      id: "zobo", name: "Chilled Zobo", cat: "sweet", badge: "Cold", price: 700,
      img: "assets/art/zobo.svg",
      alt: "Glass of iced zobo with an orange slice and a striped straw",
      desc: "Chilled hibiscus with ginger and pineapple. Cools the pepper right down.",
      heat: 1, full: 1, napkins: 0, serves: "50cl",
    },
  ],
};
