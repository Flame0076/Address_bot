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
        "districts": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Meerut", "Prayagraj", "Ghaziabad", "Noida", "Bareilly", "Gorakhpur"],
        "weight": 25,
        "pincode_prefix": ["201", "226", "208", "221", "282", "250", "211", "243", "273"]
    },
    "Bihar": {
        "districts": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Purnia", "Darbhanga", "Ara", "Begusarai", "Katihar", "Chhapra"],
        "weight": 20,
        "pincode_prefix": ["800", "823", "842", "812", "854", "846", "802", "851", "841"]
    },
    "Madhya Pradesh": {
        "districts": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain", "Sagar", "Dewas", "Satna", "Ratlam", "Rewa"],
        "weight": 20,
        "pincode_prefix": ["462", "452", "474", "482", "456", "470", "455", "485", "457"]
    },
    "Rajasthan": {
        "districts": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer", "Bikaner", "Alwar", "Bhilwara", "Sikar", "Pali"],
        "weight": 18,
        "pincode_prefix": ["302", "342", "313", "324", "305", "334", "301", "311", "332"]
    },
    "Delhi": {
        "districts": ["New Delhi", "North Delhi", "South Delhi", "West Delhi", "East Delhi", "Central Delhi"],
        "weight": 12,
        "pincode_prefix": ["110"]
    },
    "Maharashtra": {
        "districts": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Solapur", "Thane", "Kolhapur"],
        "weight": 10,
        "pincode_prefix": ["400", "411", "440", "422", "431", "413", "421"]
    },
    "Karnataka": {
        "districts": ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Belagavi", "Davangere"],
        "weight": 8,
        "pincode_prefix": ["560", "570", "580", "575", "590"]
    },
    "Gujarat": {
        "districts": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar"],
        "weight": 8,
        "pincode_prefix": ["380", "390", "360", "364", "361"]
    },
    "Punjab": {
        "districts": ["Amritsar", "Ludhiana", "Jalandhar", "Patiala", "Bathinda"],
        "weight": 6,
        "pincode_prefix": ["141", "143", "144", "147", "151"]
    },
    "Haryana": {
        "districts": ["Gurugram", "Faridabad", "Panipat", "Ambala", "Hisar", "Rohtak"],
        "weight": 6,
        "pincode_prefix": ["122", "121", "132", "133", "125", "124"]
    }
}

ROAD_NAMES = [
    "MG Road", "Station Road", "Civil Lines", "Main Market Road", "Ring Road",
    "Subhash Chowk", "Nehru Nagar Street 4", "Gandhi Path", "Hospital Road", "Temple Street",
    "Station Square", "University Road", "IT Park Avenue", "Industrial Area Phase 2", "Rajendra Nagar Main Road"
]

VILLAGE_BLOCKS = [
    "Block A, Sector 12", "Block B, Near Panchayat Ghar", "Ward No. 7", "Tehsil Road Area",
    "Extension Zone", "Green Park Colony", "Housing Board Colony", "Shanti Niketan Enclave",
    "Model Town Phase 1", "Industrial Growth Center", "Old City Zone", "Urban Estate Area"
]

user_history = {}

def get_random_address(user_id):
    states = list(STATES_DATA.keys())
    weights = [STATES_DATA[s]["weight"] for s in states]
    
    selected_state = random.choices(states, weights=weights, k=1)[0]
    state_info = STATES_DATA[selected_state]
    
    district = random.choice(state_info["districts"])
    road = random.choice(ROAD_NAMES)
    block = random.choice(VILLAGE_BLOCKS)
    
    floor = random.choice(["Ground Floor", "1st Floor", "2nd Floor", "Independent House", "Basement Floor"])
    door_no = f"House No. {random.randint(1, 450)}"
    flat_no = f"Flat/Plot {random.choice(['A', 'B', 'C', 'X', 'Y'])}-{random.randint(10, 99)}"
    
    pin_prefix = random.choice(state_info["pincode_prefix"])
    pincode = f"{pin_prefix}{random.randint(100, 999)}"
    
    address_tuple = (road, floor, door_no, flat_no, block, district, selected_state, pincode)
    
    if user_id not in user_history:
        user_history[user_id] = []
        
    if address_tuple in user_history[user_id]:
        return get_random_address(user_id)
        
    user_history[user_id].append(address_tuple)
    if len(user_history[user_id]) > 15:
        user_history[user_id].pop(0)
        
    return address_tuple

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    addr = get_random_address(user_id)
    road, floor, door, flat, block, district, state, pincode = addr
    
    response_text = (
        f"🇮🇳 **New Indian Address Generated**\n\n"
        f"🛣️ **Road Name:** {road}\n"
        f"🚪 **Floor/Door/Flat:** {floor}, {door}, {flat}\n"
        f"🏡 **Village/Block:** {block}\n"
        f"🏙️ **City/District:** {district}\n"
        f"🗺️ **State:** {state}\n"
        f"📮 **Pincode:** {pincode}\n\n"
        f"🔄 *Har baar /start dabane par ek naya aur unique address milega!*"
    )
    await update.message.reply_text(response_text, parse_mode="Markdown")

def main():
    # Start Flask server in background thread so Render detects a running port
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        logger.error("BOT_TOKEN environment variable missing!")
        return
    
    # YAHAN TIMEOUTS BADHAYE GAYE HAIN (30 Seconds)
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
    
    # Polling timeout bhi 30 set kiya hai taaki connection drop na ho
    app.run_polling(timeout=30)

if __name__ == "__main__":
    main()
