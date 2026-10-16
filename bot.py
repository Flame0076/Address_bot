import os
import random
import logging
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app for Render Web Service (Port binding)
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Telegram Address Bot is active and running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

# ----------------- DATASETS & WEIGHTED REGIONS -----------------
STATES_DATA = {
    "Uttar Pradesh": {
        "districts": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Meerut", "Prayagraj", "Ghaziabad", "Noida", "Bareilly", "Gorakhpur", "Aligarh", "Moradabad"],
        "weight": 25,
        "pincode_prefix": ["201", "226", "208", "221", "282", "250", "211", "243", "273"]
    },
    "Bihar": {
        "districts": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Purnia", "Darbhanga", "Ara", "Begusarai", "Katihar", "Chhapra", "Samastipur"],
        "weight": 20,
        "pincode_prefix": ["800", "823", "842", "812", "854", "846", "802", "851", "841"]
    },
    "Madhya Pradesh": {
        "districts": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain", "Sagar", "Dewas", "Satna", "Ratlam", "Rewa", "Katni", "Singrauli"],
        "weight": 20,
        "pincode_prefix": ["462", "452", "474", "482", "456", "470", "455", "485", "457"]
    },
    "Rajasthan": {
        "districts": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer", "Bikaner", "Alwar", "Bhilwara", "Sikar", "Pali", "Sri Ganganagar"],
        "weight": 18,
        "pincode_prefix": ["302", "342", "313", "324", "305", "334", "301", "311", "332"]
    },
    "Delhi": {
        "districts": ["New Delhi", "North Delhi", "South Delhi", "West Delhi", "East Delhi", "Central Delhi"],
        "weight": 12,
        "pincode_prefix": ["110"]
    },
    "Maharashtra": {
        "districts": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Solapur", "Thane", "Kolhapur", "Amravati"],
        "weight": 10,
        "pincode_prefix": ["400", "411", "440", "422", "431", "413", "421"]
    },
    "Karnataka": {
        "districts": ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Belagavi", "Davangere", "Ballari"],
        "weight": 8,
        "pincode_prefix": ["560", "570", "580", "575", "590"]
    }
}

# ----------------- DYNAMIC GENERATORS (Yahan se repeat hona impossible hai) -----------------

def get_dynamic_road():
    roads = ["MG Road", "Station Road", "Civil Lines", "Main Market", "Ring Road", "Subhash Chowk", "Gandhi Path", "Hospital Road", "Temple Street", "University Road", "IT Park Avenue", "Industrial Road", "Rajendra Nagar", "Patel Marg", "Nehru Street", "Ambedkar Road", "Tagore Path", "Shastri Marg", "Link Road", "Bypass Road", "Mall Road"]
    prefix = random.choice(["Street No.", "Lane No.", "Gali No.", "Road No.", "Path No."])
    num = random.randint(1, 999) # Har baar naya number aayega (e.g., Gali No. 452)
    return f"{prefix} {num}, {random.choice(roads)}"

def get_dynamic_block():
    formats = [
        f"Sector {random.randint(1, 150)}",
        f"Block {random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}-{random.randint(1, 99)}",
        f"Ward No. {random.randint(1, 200)}",
        f"Phase {random.randint(1, 10)}",
        f"Zone {random.choice(['North', 'South', 'East', 'West'])}"
    ]
    return random.choice(formats) # Har baar ek alag combination banega (e.g., Block K-72)

def get_dynamic_village():
    # Hazaron alag-alag village naam combine honge automatically
    prefixes = ["Ram", "Gopal", "Madho", "Kishan", "Shanti", "Narayan", "Govind", "Mirza", "Kalyan", "Jagdish", "Bhavani", "Sita", "Hari", "Kamal", "Lakshman", "Mohan", "Prem", "Anand", "Shiv", "Fateh", "Sultan", "Nawab", "Vijay", "Bharat", "Indira"]
    suffixes = ["pur", "nagar", "garh", "gaon", "abad", "khera", "vihar", "kunj", "talab", "wadi"]
    
    generated_name = f"{random.choice(prefixes)}{random.choice(suffixes)}"
    
    # Thodi aur reality add karne ke liye
    if random.random() > 0.5:
        return f"{generated_name} Khas"
    elif random.random() > 0.3:
        return f"{generated_name} Khurd"
    else:
        return generated_name

FLOORS = ["Ground Floor", "1st Floor", "2nd Floor", "3rd Floor", "4th Floor", "Upper Ground Floor"]

# Ab history track karne ki zaroorat hi nahi, kyuki combination karodo mein hain
def get_random_address():
    # Select state based on weight
    states = list(STATES_DATA.keys())
    weights = [STATES_DATA[s]["weight"] for s in states]
    
    selected_state = random.choices(states, weights=weights, k=1)[0]
    state_info = STATES_DATA[selected_state]
    
    # Select components dynamically
    district = random.choice(state_info["districts"])
    city = district 
    
    road = get_dynamic_road()
    village = get_dynamic_village()
    block = get_dynamic_block()
    floor = random.choice(FLOORS)
    
    pin_prefix = random.choice(state_info["pincode_prefix"])
    pincode = f"{pin_prefix}{random.randint(100, 999)}"
    
    return (road, floor, village, block, city, district, selected_state, pincode)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    addr = get_random_address()
    road, floor, village, block, city, district, state, pincode = addr
    
    # Bilkul wahi format jo aapne manga tha
    response_text = (
        f"Road Name: {road}\n"
        f"Floor: {floor}\n"
        f"Village: {village}\n"
        f"Block: {block}\n"
        f"City: {city}\n"
        f"District: {district}\n"
        f"State: {state}\n"
        f"Pincode: {pincode}"
    )
    
    await update.message.reply_text(response_text)

def main():
    # Start Flask server in background thread so Render detects a running port
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        logger.error("BOT_TOKEN environment variable missing!")
        return
    
    # Timeouts set hain taaki server crash na ho
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .pool_timeout(30.0)
        .build()
    )
    
    app.add_handler(CommandHandler("start", start_command))
    
    logger.info("Telegram Bot started polling...")
    app.run_polling(timeout=30)

if __name__ == "__main__":
    main()
