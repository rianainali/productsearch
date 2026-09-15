import asyncio
import logging
import time

from google.genai.errors import ClientError

from embedding_service import EmbeddingService
from models import ProductData
from vector_store import InMemoryVectorStore

logger = logging.getLogger(__name__)

SEED_PRODUCTS: list[ProductData] = [
    # --- Electronics ---
    ProductData(
        title="Wireless Bluetooth Headphones",
        description="Over-ear noise-cancelling headphones with deep bass and 40-hour battery life. Foldable design for easy transport.",
        characteristics=["Bluetooth 5.3", "ANC", "40h battery", "foldable", "built-in mic"],
        price=79.99,
    ),
    ProductData(
        title="4K Ultra HD Smart TV 55 inch",
        description="55-inch LED smart TV with HDR10+ support, built-in streaming apps, and Dolby Atmos sound.",
        characteristics=["4K UHD", "HDR10+", "Dolby Atmos", "smart TV", "55 inch"],
        price=499.99,
    ),
    ProductData(
        title="Portable Bluetooth Speaker",
        description="Waterproof portable speaker with 360-degree sound, 12-hour playtime, and RGB lighting effects.",
        characteristics=["waterproof IP67", "360 sound", "12h battery", "RGB lights", "Bluetooth 5.0"],
        price=49.99,
    ),
    ProductData(
        title="Wireless Gaming Mouse",
        description="Ergonomic gaming mouse with 16000 DPI optical sensor, 6 programmable buttons, and RGB lighting.",
        characteristics=["16000 DPI", "wireless", "ergonomic", "RGB", "6 buttons", "rechargeable"],
        price=59.99,
    ),
    ProductData(
        title="USB-C Fast Charging Cable 2m",
        description="Braided nylon USB-C to USB-C cable supporting 100W fast charging and 10Gbps data transfer.",
        characteristics=["USB-C", "100W charging", "10Gbps", "2 meters", "braided nylon"],
        price=14.99,
    ),
    # --- Clothing ---
    ProductData(
        title="Men's Running Shoes",
        description="Lightweight mesh running shoes with responsive foam cushioning and breathable upper. Ideal for road running.",
        characteristics=["lightweight", "mesh upper", "foam cushioning", "breathable", "road running"],
        price=89.99,
    ),
    ProductData(
        title="Women's Winter Down Jacket",
        description="Warm insulated down jacket with water-resistant shell, detachable hood, and zippered pockets.",
        characteristics=["down insulation", "water-resistant", "detachable hood", "zippered pockets", "warm"],
        price=129.99,
    ),
    ProductData(
        title="Classic Cotton T-Shirt",
        description="Soft 100% organic cotton crew-neck t-shirt. Pre-shrunk fabric, available in multiple colors.",
        characteristics=["100% organic cotton", "crew neck", "pre-shrunk", "unisex", "machine washable"],
        price=19.99,
    ),
    # --- Home & Kitchen ---
    ProductData(
        title="Stainless Steel French Press",
        description="Double-wall insulated French press coffee maker. Keeps coffee hot for hours. 1-liter capacity.",
        characteristics=["stainless steel", "double-wall", "insulated", "1 liter", "dishwasher safe"],
        price=34.99,
    ),
    ProductData(
        title="Robot Vacuum Cleaner",
        description="Smart robot vacuum with laser navigation, 2500Pa suction, and automatic dust emptying station.",
        characteristics=["laser navigation", "2500Pa suction", "auto empty", "app control", "150min runtime"],
        price=349.99,
    ),
    ProductData(
        title="LED Desk Lamp with Wireless Charger",
        description="Adjustable LED desk lamp with 5 brightness levels, 3 color temperatures, and built-in Qi wireless charger.",
        characteristics=["LED", "5 brightness levels", "3 color temps", "Qi charger", "touch control"],
        price=44.99,
    ),
    # --- Sports & Outdoors ---
    ProductData(
        title="Yoga Mat 6mm Non-Slip",
        description="Eco-friendly TPE yoga mat with alignment lines. Non-slip surface on both sides. Includes carry strap.",
        characteristics=["6mm thick", "TPE material", "non-slip", "alignment lines", "carry strap"],
        price=29.99,
    ),
    ProductData(
        title="Insulated Water Bottle 750ml",
        description="Double-wall vacuum insulated stainless steel bottle. Keeps drinks cold 24h or hot 12h. BPA-free.",
        characteristics=["750ml", "vacuum insulated", "stainless steel", "BPA-free", "cold 24h / hot 12h"],
        price=24.99,
    ),
    ProductData(
        title="Adjustable Dumbbell Set 20kg",
        description="Space-saving adjustable dumbbell pair with quick-lock mechanism. Weight range from 2kg to 20kg per dumbbell.",
        characteristics=["adjustable 2-20kg", "quick-lock", "space-saving", "pair included", "steel plates"],
        price=149.99,
    ),
    # --- Books & Office ---
    ProductData(
        title="Mechanical Keyboard RGB",
        description="Compact 75% mechanical keyboard with hot-swappable switches, PBT keycaps, and per-key RGB backlighting.",
        characteristics=["75% layout", "hot-swappable", "PBT keycaps", "RGB backlight", "USB-C"],
        price=69.99,
    ),
    ProductData(
        title="Ergonomic Office Chair",
        description="Adjustable mesh office chair with lumbar support, headrest, and 4D armrests. Supports up to 150kg.",
        characteristics=["mesh back", "lumbar support", "headrest", "4D armrests", "150kg capacity"],
        price=279.99,
    ),
]


async def load_seed_products(
    store: InMemoryVectorStore,
    embed_svc: EmbeddingService,
    max_retries: int = 3,
) -> None:
    start = time.time()
    total = len(SEED_PRODUCTS)
    logger.info("Loading %d seed products...", total)

    for i, product in enumerate(SEED_PRODUCTS):
        for attempt in range(max_retries):
            try:
                embedding = embed_svc.embed_product(product)
                store.add(product, embedding)
                logger.info("[%d/%d] Loaded: %s", i + 1, total, product.title)
                break
            except ClientError as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    wait = 2 ** (attempt + 1)
                    logger.warning("Rate limited, retrying in %ds...", wait)
                    await asyncio.sleep(wait)
                else:
                    raise

    elapsed = time.time() - start
    logger.info("Seed loading complete: %d products in %.1fs", store.count, elapsed)
