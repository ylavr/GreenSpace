import os
import shutil
from tqdm import tqdm

def count_images_in_directory(base_dir):
    total_images = 0
    species_counts = {}
    for species in os.listdir(base_dir):
        species_dir = os.path.join(base_dir, species)
        if os.path.isdir(species_dir):
            image_files = [f for f in os.listdir(species_dir)
                           if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'))]
            species_counts[species] = len(image_files)
            total_images += len(image_files)
    return total_images, species_counts

def move_images(source_base_dir, target_base_dir):
    # List of species (folder names)
    species_list = [
        'African_Violet_Saintpaulia_ionantha', 'Aloe_Vera', 'Anthurium_Anthurium_andraeanum',
        'Areca_Palm_Dypsis_lutescens', 'Asparagus_Fern_Asparagus_setaceus', 'Begonia_Begonia_spp',
        'Birds_Nest_Fern_Asplenium_nidus', 'Bird_of_Paradise_Strelitzia_reginae', 'Boston_Fern_Nephrolepis_exaltata',
        'Calathea', 'Cast_Iron_Plant_Aspidistra_elatior', 'Chinese_evergreen_Aglaonema', 'Chinese_Money_Plant_Pilea_peperomioides',
        'Christmas_Cactus_Schlumbergera_bridgesii', 'Chrysanthemum', 'Ctenanthe', 'Daffodils_Narcissus_spp', 'Dracaena',
        'Dumb_Cane_Dieffenbachia_spp', 'Elephant_Ear_Alocasia_spp', 'English_Ivy_Hedera_helix', 'Hyacinth_Hyacinthus_orientalis',
        'Iron_Cross_begonia_Begonia_masoniana', 'Jade_plant_Crassula_ovata', 'Kalanchoe', 'Lilium_Hemerocallis',
        'Lily_of_the_valley_Convallaria_majalis', 'Money_Tree_Pachira_aquatica', 'Monstera_Deliciosa_Monstera_deliciosa',
        'Orchid', 'Parlor_Palm_Chamaedorea_elegans', 'Peace_lily', 'Poinsettia_Euphorbia_pulcherrima', 'Polka_Dot_Plant_Hypoestes_phyllostachya',
        'Ponytail_Palm_Beaucarnea_recurvata', 'Pothos_Ivy_arum', 'Prayer_Plant_Maranta_leuconeura', 'Rattlesnake_Plant_Calathea_lancifolia',
        'Rubber_Plant_Ficus_elastica', 'Sago_Palm_Cycas_revoluta', 'Schefflera', 'Snake_plant_Sanseviera', 'Tradescantia', 'Tulip',
        'Venus_Flytrap', 'Yucca', 'ZZ_Plant_Zamioculcas_zamiifolia'
    ]

    for species in species_list:
        source_species_folder = os.path.join(source_base_dir, species)
        target_species_folder = os.path.join(target_base_dir, species)

        if not os.path.exists(source_species_folder):
            print(f"Source folder does not exist: {source_species_folder}")
            continue

        if not os.path.exists(target_species_folder):
            print(f"Target folder does not exist: {target_species_folder}. Creating it.")
            os.makedirs(target_species_folder, exist_ok=True)

        # List of image files in the source species folder
        image_files = [f for f in os.listdir(source_species_folder)
                       if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'))]

        for image_file in tqdm(image_files, desc=f"Moving images for {species}"):
            source_image_path = os.path.join(source_species_folder, image_file)
            target_image_path = os.path.join(target_species_folder, image_file)

            # Check if the file already exists in the target folder
            if os.path.exists(target_image_path):
                # If the file exists, rename the source file to avoid overwriting
                base, ext = os.path.splitext(image_file)
                new_image_file = f"{base}_copy{ext}"
                target_image_path = os.path.join(target_species_folder, new_image_file)

            # Move the image
            shutil.move(source_image_path, target_image_path)

        print(f"Moved images from {source_species_folder} to {target_species_folder}")

if __name__ == "__main__":
    source_base_dir = 'dataset'
    target_base_dir = 'house_plant_species'

    # Count images before the move
    print("Counting images before the move...\n")
    dataset_total_before, dataset_species_counts_before = count_images_in_directory(source_base_dir)
    houseplant_total_before, houseplant_species_counts_before = count_images_in_directory(target_base_dir)

    print(f"Total images in '{source_base_dir}' before move: {dataset_total_before}")
    print(f"Total images in '{target_base_dir}' before move: {houseplant_total_before}\n")

    # Optionally, print counts per species
    print("Images per species in 'dataset' before move:")
    for species, count in dataset_species_counts_before.items():
        print(f"{species}: {count}")
    print("\n")

    print("Images per species in 'house_plant_species' before move:")
    for species, count in houseplant_species_counts_before.items():
        print(f"{species}: {count}")
    print("\n")

    # Move the images
    print("Moving images...\n")
    move_images(source_base_dir, target_base_dir)

    # Count images after the move
    print("\nCounting images after the move...\n")
    dataset_total_after, dataset_species_counts_after = count_images_in_directory(source_base_dir)
    houseplant_total_after, houseplant_species_counts_after = count_images_in_directory(target_base_dir)

    print(f"Total images in '{source_base_dir}' after move: {dataset_total_after}")
    print(f"Total images in '{target_base_dir}' after move: {houseplant_total_after}\n")

    # Optionally, print counts per species
    print("Images per species in 'dataset' after move:")
    for species, count in dataset_species_counts_after.items():
        print(f"{species}: {count}")
    print("\n")

    print("Images per species in 'house_plant_species' after move:")
    for species, count in houseplant_species_counts_after.items():
        print(f"{species}: {count}")
    print("\n")
