/*
 * Everything a non-developer is likely to change lives here: prices, dishes,
 * cravings, contact numbers. Prices are in naira and match the Chowdeck menu.
 *
 * Photos: put a photo in assets/img/ and set `img` to its path plus
 * `photo: true` (photos get a framed, rounded crop; illustrations are cut-outs).
 * A dish with `price: null` is kept here but hidden on the site until priced.
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
    { id: "rice", label: "Rice & more" },
    { id: "swallow", label: "Swallow & soup" },
    { id: "protein", label: "Protein" },
    { id: "sides", label: "Sides" },
  ],

  cravings: [
    { label: "Starving", dish: "jollof-enjoyment" },
    { label: "Spicy", dish: "bokoto" },
    { label: "Swallow", dish: "amala-feast" },
    { label: "Fish", dish: "eja-kika" },
    { label: "Meaty", dish: "assorted-meat" },
    { label: "On a budget", dish: "jollof-rice" },
  ],

  // heat / full / napkins are 0-5 ratings shown on the craving card.
  dishes: [
    // Rice & more
    {
      id: "jollof-enjoyment", name: "Jollof Enjoyment Combo", cat: "rice", badge: "Combo", price: 6000,
      img: "assets/art/jollof-enjoyment.svg",
      alt: "Jollof rice with fried plantain, two pieces of beef and a boiled egg",
      desc: "Jollof rice, plantain, two pieces of beef and an egg.",
      heat: 3, full: 5, napkins: 3, serves: "Combo",
    },
    {
      id: "royal-basmati", name: "Royal Basmati Combo", cat: "rice", badge: "Combo", price: 6000,
      img: "assets/art/royal-basmati.svg",
      alt: "Basmati fried rice with two pieces of beef and fried plantain",
      desc: "Basmati rice with two pieces of beef and plantain.",
      heat: 2, full: 5, napkins: 3, serves: "Combo",
    },
    {
      id: "white-rice-special", name: "White Rice Special", cat: "rice", badge: "Combo", price: 6000,
      img: "assets/art/white-rice-special.svg",
      alt: "White rice and stew with plantain, egg, beef and assorted meat",
      desc: "White rice, plantain, one egg, one meat and one assorted meat.",
      heat: 3, full: 5, napkins: 3, serves: "Combo",
    },
    {
      id: "ofada-special", name: "Ofada Special Combo", cat: "rice", badge: "Combo", price: 6000,
      img: "assets/art/ofada-special.svg",
      alt: "Ofada rice with egg, fried plantain and assorted meats",
      desc: "Ofada rice, egg, plantain and assorted meats.",
      heat: 4, full: 5, napkins: 3, serves: "Combo",
    },
    {
      id: "chicken-chips", name: "Chicken & Chips Delight", cat: "rice", badge: "Combo", price: 9000,
      img: "assets/art/chicken-chips.svg",
      alt: "Fried chicken drumsticks with golden chips and ketchup",
      desc: "Juicy fried chicken paired with crispy golden chips.",
      heat: 1, full: 4, napkins: 4, serves: "Combo",
    },
    {
      id: "basmati-fried-rice", name: "Basmati Fried Rice", cat: "rice", badge: "", price: 2000,
      img: "assets/art/basmati-fried-rice.svg",
      alt: "Basmati fried rice with peas and carrots",
      desc: "Our special fried rice, made with basmati.",
      heat: 1, full: 3, napkins: 1, serves: "Plate",
    },
    {
      id: "jollof-rice", name: "Jollof Rice", cat: "rice", badge: "", price: 800,
      img: "assets/art/jollof-rice.svg",
      alt: "Plate of jollof rice",
      desc: "Delicious jollof rice, served plain without protein.",
      heat: 2, full: 3, napkins: 1, serves: "Plate",
    },
    {
      id: "ofada-rice", name: "Ofada", cat: "rice", badge: "", price: 800,
      img: "assets/art/ofada-rice.svg",
      alt: "Plate of native ofada rice",
      desc: "Native ofada rice.",
      heat: 0, full: 3, napkins: 1, serves: "Plate",
    },
    {
      id: "stir-fry-spaghetti", name: "Stir Fry Spaghetti", cat: "rice", badge: "", price: 2000,
      img: "assets/art/stir-fry-spaghetti.svg",
      alt: "Stir-fried spaghetti with peppers and sausage",
      desc: "Stir-fried spaghetti, peppers and all.",
      heat: 2, full: 3, napkins: 2, serves: "Plate",
    },
    {
      id: "porridge", name: "Yam Porridge", cat: "rice", badge: "", price: 1000,
      img: "assets/art/porridge.svg",
      alt: "Yam porridge in red pepper sauce with greens",
      desc: "Freshly prepared yam porridge.",
      heat: 3, full: 4, napkins: 2, serves: "Plate",
    },

    // Swallow & soup
    {
      id: "amala-feast", name: "Amala Swallow Feast", cat: "swallow", badge: "Combo", price: 5000,
      img: "assets/art/amala-feast.svg",
      alt: "Two wraps of amala with ewedu, gbegiri and meat",
      desc: "Amala (two wraps) served with ewedu, gbegiri and two pieces of meat.",
      heat: 3, full: 5, napkins: 2, serves: "Combo",
    },
    {
      id: "semo-combo", name: "Semo Combo", cat: "swallow", badge: "Combo", price: 4000,
      img: "assets/art/semo-combo.svg",
      alt: "Semo with efo riro, two pieces of meat and ponmo",
      desc: "Semo, efo riro, two pieces of meat and ponmo.",
      heat: 3, full: 5, napkins: 2, serves: "Combo",
    },
    {
      id: "eba", name: "Eba", cat: "swallow", badge: "", price: 500,
      img: "assets/art/eba.svg", alt: "Wrap of eba",
      desc: "Soft, smooth and freshly prepared eba.",
      heat: 0, full: 4, napkins: 1, serves: "Swallow",
    },
    {
      id: "fufu", name: "Fufu", cat: "swallow", badge: "", price: 500,
      img: "assets/art/fufu.svg", alt: "Wrap of fufu",
      desc: "Our soft and stretchy fufu.",
      heat: 0, full: 4, napkins: 1, serves: "Swallow",
    },
    {
      id: "semo", name: "Semo", cat: "swallow", badge: "", price: 500,
      img: "assets/art/semo.svg", alt: "Wrap of semo",
      desc: "Soft, smooth and freshly prepared semo.",
      heat: 0, full: 4, napkins: 1, serves: "Swallow",
    },
    {
      id: "egusi", name: "Egusi", cat: "swallow", badge: "Soup", price: 500,
      img: "assets/art/egusi.svg", alt: "Egusi soup with greens and meat",
      desc: "Flavourful egusi soup.",
      heat: 2, full: 3, napkins: 2, serves: "Soup",
    },
    {
      id: "efo-riro", name: "Efo Riro", cat: "swallow", badge: "Soup", price: 500,
      img: "assets/art/efo-riro.svg", alt: "Efo riro vegetable soup with meat and ponmo",
      desc: "Flavourful Yoruba vegetable soup.",
      heat: 3, full: 3, napkins: 2, serves: "Soup",
    },

    // Protein
    {
      id: "turkey", name: "Turkey", cat: "protein", badge: "", price: 7000,
      img: "assets/img/turkey.jpg", photo: true, alt: "Three fried turkey wings",
      desc: "Fried turkey.",
      heat: 2, full: 3, napkins: 5, serves: "Protein",
    },
    {
      id: "fried-chicken", name: "Fried Chicken", cat: "protein", badge: "", price: null,
      img: "assets/art/fried-chicken.svg", alt: "Fried chicken drumsticks",
      desc: "Golden, juicy chicken.",
      heat: 1, full: 3, napkins: 4, serves: "Protein",
    },
    {
      id: "bokoto", name: "Bokoto", cat: "protein", badge: "Peppered", price: 4500,
      img: "assets/art/bokoto.svg", alt: "Peppered cow foot in red pepper sauce",
      desc: "Peppered cow meat.",
      heat: 5, full: 3, napkins: 5, serves: "Protein",
    },
    {
      id: "asun", name: "Asun Goat Meat", cat: "protein", badge: "Peppered", price: 3500,
      img: "assets/art/asun.svg", alt: "Peppered goat meat with onions and peppers",
      desc: "Succulent pieces of goat meat, peppered asun style.",
      heat: 5, full: 3, napkins: 4, serves: "Protein",
    },
    {
      id: "croaker", name: "Croaker Fish", cat: "protein", badge: "", price: 3500,
      img: "assets/art/croaker.svg", alt: "Whole croaker fish in pepper sauce",
      desc: "Well-seasoned croaker fish.",
      heat: 3, full: 3, napkins: 4, serves: "Protein",
    },
    {
      id: "eja-kika", name: "Eja Kika", cat: "protein", badge: "Peppered", price: 3000,
      img: "assets/art/eja-kika.svg", alt: "Peppered fish in red pepper sauce",
      desc: "Peppered eja kika.",
      heat: 4, full: 3, napkins: 4, serves: "Protein",
    },
    {
      id: "beef", name: "Beef", cat: "protein", badge: "Peppered", price: 2000,
      img: "assets/art/beef.svg", alt: "Peppered beef with green peppers and onions",
      desc: "Peppered meat.",
      heat: 4, full: 2, napkins: 3, serves: "Protein",
    },
    {
      id: "assorted-meat", name: "Assorted Meat", cat: "protein", badge: "", price: 500,
      img: "assets/art/assorted-meat.svg", alt: "Shaki, liver and roundabout in pepper sauce",
      desc: "Shaki, liver and roundabout.",
      heat: 3, full: 2, napkins: 3, serves: "Protein",
    },
    {
      id: "ponmo", name: "Ponmo", cat: "protein", badge: "Peppered", price: 500,
      img: "assets/art/ponmo.svg", alt: "Peppered ponmo in red pepper sauce",
      desc: "Peppered ponmo.",
      heat: 4, full: 1, napkins: 3, serves: "Protein",
    },

    // Sides
    {
      id: "plantain", name: "Plantain", cat: "sides", badge: "Side", price: 1000,
      img: "assets/art/plantain.svg", alt: "Plate of sweet fried plantain",
      desc: "Sweet fried plantain, per portion.",
      heat: 0, full: 2, napkins: 2, serves: "Per portion",
    },
    {
      id: "salad", name: "Salad", cat: "sides", badge: "Side", price: 1000,
      img: "assets/art/salad.svg", alt: "Fresh coleslaw with cabbage and carrots",
      desc: "Fresh salad.",
      heat: 0, full: 1, napkins: 1, serves: "Side",
    },
    {
      id: "moi-moi", name: "Moimoi", cat: "sides", badge: "Side", price: 500,
      img: "assets/art/moi-moi.svg", alt: "Moimoi with boiled egg on a leaf",
      desc: "Soft, full-of-flavour moimoi.",
      heat: 2, full: 3, napkins: 1, serves: "Side",
    },
  ],
};
