/*
 * Supabase connection, shared by the website and the admin dashboard.
 * Both values are in Supabase → Project Settings → API (or "API Keys"):
 *   supabaseUrl: the Project URL, e.g. "https://abcdefgh.supabase.co"
 *   supabaseKey: the anon / publishable key (NOT the service_role / secret key)
 *
 * The anon key is meant to be public. What it can do is limited by the rules
 * in supabase/setup.sql. While these are empty the site uses the menu in
 * js/data.js and the bag falls back to visit / call / WhatsApp.
 */
window.IYA_CONFIG = {
  supabaseUrl: "https://qmnqhudahvaxmqigrepg.supabase.co",
  supabaseKey: "sb_publishable_tqwbiYJuN78QD4t6N8oLMQ_23uc5_gc",
};
