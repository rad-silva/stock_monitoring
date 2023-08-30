import random

def generate_random_product():
    kit_base_parts = 43
    min_variation_parts = 20
    max_variation_parts = 33
    total_parts = 100

    # Generate random number of parts for the kit variation
    kit_variation_parts = random.randint(min_variation_parts, max_variation_parts)

    # Generate a list of zeros representing the product configuration
    product_config = [0] * total_parts

    # Assign parts to the kit base
    for i in range(kit_base_parts):
        product_config[i] = 1

    # Assign parts to the kit variation
    available_positions = list(range(total_parts))
    available_positions = [pos for pos in available_positions if product_config[pos] == 0]  # Filter out used positions
    for i in range(kit_variation_parts):
        random_position = random.choice(available_positions)
        product_config[random_position] = 1
        available_positions.remove(random_position)

    return product_config

# Generate a random product configuration
random_product = generate_random_product()
print(random_product)





