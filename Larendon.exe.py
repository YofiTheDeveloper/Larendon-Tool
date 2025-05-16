import datetime
import time
import os
import sys
import re
import logging

# --- Konfiguracja Logowania ---
LOG_FILE_NAME = "skrypt_log.txt"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=LOG_FILE_NAME,
    filemode='a'
)

# --- Funkcja do czyszczenia ekranu konsoli ---
def clear_screen():
    """Czyści ekran konsoli."""
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

# --- Funkcja do drukowania tekstu z pionowym gradientem (dla ASCII art) ---
def print_vertical_gradient_text(text, start_color_rgb, end_color_rgb):
    lines = text.splitlines()
    num_lines = len(lines)
    if num_lines == 0: return
    for i, line in enumerate(lines):
        ratio = i / (num_lines - 1) if num_lines > 1 else 0
        r = int(start_color_rgb[0] * (1 - ratio) + end_color_rgb[0] * ratio)
        g = int(start_color_rgb[1] * (1 - ratio) + end_color_rgb[1] * ratio)
        b = int(start_color_rgb[2] * (1 - ratio) + end_color_rgb[2] * ratio)
        print(f"\033[38;2;{r};{g};{b}m{line}\033[0m")

# --- Funkcja do aplikowania poziomego gradientu do pojedynczego słowa ---
def apply_horizontal_gradient_to_word(word, color1_rgb, color2_rgb):
    colored_word = ""
    n = len(word)
    if n == 0: return ""
    if n == 1:
        r, g, b = color1_rgb
        return f"\033[38;2;{r};{g};{b}m{word}\033[0m"
    for i, char in enumerate(word):
        ratio = i / (n - 1) if n > 1 else 0
        r = int(color1_rgb[0] * (1 - ratio) + color2_rgb[0] * ratio)
        g = int(color1_rgb[1] * (1 - ratio) + color2_rgb[1] * ratio)
        b = int(color1_rgb[2] * (1 - ratio) + color2_rgb[2] * ratio)
        colored_word += f"\033[38;2;{r};{g};{b}m{char}"
    return colored_word + "\033[0m"

# --- Funkcja do wyświetlania animowanej linii (dla Info/Config/Caution/Done) ---
def print_animated_line(prefix_text, animated_word, suffix_text, gradient_cycle, duration_sec, fps, final_newline=False, log_level=logging.INFO, log_message_override=None, clear_line_before=False):
    if clear_line_before:
        sys.stdout.write(f"\r\033[K") # Wyczyść bieżącą linię przed rozpoczęciem animacji
        sys.stdout.flush()

    log_content = f"{prefix_text.strip()} {animated_word} {suffix_text.strip()}"
    if log_message_override:
        log_content = log_message_override
    cleaned_log_content = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} I ', '', log_content)
    cleaned_log_content = cleaned_log_content.replace(f"{animated_word} I", "").strip()
    logging.log(log_level, cleaned_log_content)

    total_frames = int(duration_sec * fps)
    num_color_states = len(gradient_cycle)
    if num_color_states == 0:
        sys.stdout.write(f"\r{prefix_text}{animated_word}{suffix_text}\033[K")
        sys.stdout.flush()
        if final_newline: print()
        return

    for frame in range(total_frames):
        color_state_index = (frame * num_color_states // total_frames) % num_color_states if total_frames > 0 else 0
        current_gradient_start, current_gradient_end = gradient_cycle[color_state_index]
        colored_animated_word = apply_horizontal_gradient_to_word(animated_word, current_gradient_start, current_gradient_end)
        sys.stdout.write(f"\r{prefix_text}{colored_animated_word}{suffix_text}\033[K")
        sys.stdout.flush()
        time.sleep(1.0 / fps if fps > 0 else 0.01)

    final_gradient_start, final_gradient_end = gradient_cycle[0]
    final_colored_word = apply_horizontal_gradient_to_word(animated_word, final_gradient_start, final_gradient_end)
    # Zawsze czyść linię przed finalnym wypisaniem, aby uniknąć artefaktów z input()
    sys.stdout.write(f"\r{prefix_text}{final_colored_word}{suffix_text}\033[K")
    sys.stdout.flush()
    if final_newline: print()


# --- Funkcja pobierająca aktualny czas jako string ---
def get_time_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- Definicje kolorów gradientów ---
green_dark_anim = (0, 120, 0)
green_medium_anim = (0, 200, 0)
green_bright_anim = (80, 255, 80)
green_gradient_cycle = [
    (green_dark_anim, green_medium_anim), (green_medium_anim, green_bright_anim),
    (green_bright_anim, green_medium_anim), (green_medium_anim, green_dark_anim)
]
red_dark_anim = (120, 0, 0)
red_medium_anim = (200, 0, 0)
red_bright_anim = (255, 80, 80)
red_gradient_cycle = [
    (red_dark_anim, red_medium_anim), (red_medium_anim, red_bright_anim),
    (red_bright_anim, red_medium_anim), (red_medium_anim, red_dark_anim)
]
yellow_dark_anim = (200, 100, 0)
yellow_medium_anim = (255, 165, 0)
yellow_bright_anim = (255, 200, 50)
caution_gradient_cycle = [
    (yellow_dark_anim, yellow_medium_anim), (yellow_medium_anim, yellow_bright_anim),
    (yellow_bright_anim, yellow_medium_anim), (yellow_medium_anim, yellow_dark_anim)
]
done_gradient_cycle = green_gradient_cycle

# Parametry animacji
ANIM_DURATION = 0.8 # Skróciłem trochę dla szybszego feedbacku przy logowaniu
ANIM_FPS = 25

# --- Funkcja pomocnicza do konwersji na CamelCase ---
def to_camel_case_for_class(text):
    if not text: return "MyPlugin"
    s = re.sub(r'[^a-zA-Z0-9_]+', ' ', text)
    parts = s.split()
    if not parts: return "MyPlugin"
    return "".join(p[0].upper() + p[1:].lower() if len(p)>1 else p.upper() for p in parts)

# --- Funkcja do zapisu zawartości do pliku ---
def write_file_content(file_path, content):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info(f"Successfully written to file: {file_path}")
    except IOError as e:
        logging.error(f"Failed to write to file {file_path}: {e}")
        raise

# --- Globalny licznik dla efektu migotania wskaźnika postępu ---
global_progress_anim_frame = 0

# --- Funkcja generująca startowe foldery i pliki ---
def generate_starter_files_and_folders(base_path, group_id_str, artifact_id_str, project_display_name, author_original_name):
    global global_progress_anim_frame
    logging.info(f"Starting generation of project files in '{base_path}' for {project_display_name} by {author_original_name}")

    group_id_parts = group_id_str.split('.')
    artifact_id_package_name = re.sub(r'[^a-z0-9_]', '', artifact_id_str.lower())
    if not artifact_id_package_name: artifact_id_package_name = "plugin"

    full_package_as_list = group_id_parts + [artifact_id_package_name]
    java_package_dir_path = os.path.join(base_path, "src", "main", "java", *full_package_as_list)
    resources_dir_path = os.path.join(base_path, "src", "main", "resources")

    main_class_name_java = to_camel_case_for_class(artifact_id_str)
    main_class_filename = f"{main_class_name_java}.java"
    fully_qualified_main_class = ".".join(full_package_as_list + [main_class_name_java])

    tasks = []
    try:
        tasks.append((
            "Directories: src/main/java/... (package structure)",
            lambda: (os.makedirs(java_package_dir_path, exist_ok=True), logging.info(f"Ensured directory exists: {java_package_dir_path}"))
        ))
        tasks.append((
            "Directory: src/main/resources",
            lambda: (os.makedirs(resources_dir_path, exist_ok=True), logging.info(f"Ensured directory exists: {resources_dir_path}"))
        ))
    except Exception as e:
        logging.error(f"Error preparing directory creation tasks: {e}")

    plugin_yml_content_str = f"""name: {project_display_name}
version: 1.0-SNAPSHOT
main: {fully_qualified_main_class}
api-version: 1.19
author: {author_original_name}
description: A starter plugin for {project_display_name}.
# commands:
#   mycommand:
#     description: An example command.
#     usage: /<command>
# permissions:
#   myplugin.mypermission:
#     description: Allows something.
#     default: op
"""
    plugin_yml_target_path = os.path.join(resources_dir_path, "plugin.yml")
    tasks.append(("File: plugin.yml", lambda: write_file_content(plugin_yml_target_path, plugin_yml_content_str)))

    main_java_file_content_str = f"""package {'.'.join(full_package_as_list)};

import org.bukkit.plugin.java.JavaPlugin;

public final class {main_class_name_java} extends JavaPlugin {{

    @Override
    public void onEnable() {{
        getLogger().info("{project_display_name} (v" + getDescription().getVersion() + ") has been enabled!");
        // Example:getServer().getPluginManager().registerEvents(new MyListener(), this);
        // Example: getCommand("mycommand").setExecutor(new MyCommandExecutor());
    }}

    @Override
    public void onDisable() {{
        getLogger().info("{project_display_name} has been disabled.");
    }}
}}
"""
    main_java_file_target_path = os.path.join(java_package_dir_path, main_class_filename)
    tasks.append((f"File: {main_class_filename}", lambda: write_file_content(main_java_file_target_path, main_java_file_content_str)))

    total_tasks_count = len(tasks)
    completed_tasks_count = 0

    progress_shimmer_colors = [
        (green_dark_anim, green_medium_anim),
        (green_medium_anim, green_bright_anim),
        (green_bright_anim, green_medium_anim)
    ]

    print()
    for i, task_item in enumerate(tasks):
        task_description, task_action = task_item
        try:
            if isinstance(task_action, tuple) and callable(task_action[0]):
                task_action[0]()
                if len(task_action) > 1 and callable(task_action[1]):
                    task_action[1]()
            elif callable(task_action):
                task_action()
            else:
                logging.error(f"Task action for '{task_description}' is not callable or a valid tuple.")
                raise TypeError(f"Task action for '{task_description}' is not correctly defined.")
            completed_tasks_count += 1
        except Exception as e:
            current_time_err = get_time_str()
            error_message = f"Task '{task_description}' failed: {e}"
            logging.error(error_message)
            sys.stdout.write(f"\r\033[K")
            print(f"{current_time_err} I Error I {error_message}")

        current_progress = int((completed_tasks_count / total_tasks_count) * 100) if total_tasks_count > 0 else 0
        global_progress_anim_frame += 1
        refresh_idx = global_progress_anim_frame % len(progress_shimmer_colors)
        refresh_col1, refresh_col2 = progress_shimmer_colors[refresh_idx]
        animated_refresh_char = apply_horizontal_gradient_to_word("↺", refresh_col1, refresh_col2)

        percent_idx = (global_progress_anim_frame + 1) % len(progress_shimmer_colors)
        percent_col1, percent_col2 = progress_shimmer_colors[percent_idx]
        animated_percent_str = apply_horizontal_gradient_to_word(f"{current_progress}%", percent_col1, percent_col2)

        max_desc_len = 30
        display_desc = task_description if len(task_description) <= max_desc_len else task_description[:max_desc_len-3] + "..."
        progress_line = f"{animated_refresh_char} │ Creating: {animated_percent_str} ({display_desc})"
        sys.stdout.write(f"\r{progress_line}{' ' * 15}\033[K")
        sys.stdout.flush()
        time.sleep(0.3)

    sys.stdout.write(f"\r\033[K")
    sys.stdout.flush()
    logging.info("Finished generation of project files.")

# --- Funkcja logowania ---
def main_login_sequence():
    login_ascii_art = """
 ___      _______  _______  ___   __    _
|   |    |       ||       ||   | |  |  | |
|   |    |   _   ||    ___||   | |   |_| |
|   |    |  | |  ||   | __ |   | |       |
|   |___ |  |_|  ||   ||  ||   | |  _    |
|       ||       ||   |_| ||   | | | |   |
|_______||_______||_______||___| |_|  |__|
"""
    login_art_start_color = (139, 0, 0)
    login_art_end_color = (255, 0, 0)

    clear_screen() # Czyść ekran NA SAMYM POCZĄTKU sekwencji logowania
    if login_ascii_art.startswith('\n'): login_ascii_art = login_ascii_art[1:]
    print_vertical_gradient_text(login_ascii_art, login_art_start_color, login_art_end_color)
    print() # Pusta linia po ASCII art

    correct_key = "Uf_Ve2$ds_.23.2dj"
    current_time_login = get_time_str()
    login_prompt_prefix = f"{current_time_login} I "
    login_prompt_suffix = " I Valid Key: "

    # Upewnij się, że linia jest czysta przed input()
    # print_animated_line już to robi (czyści linię \r i \033[K)
    print_animated_line(login_prompt_prefix, "Login", login_prompt_suffix, red_gradient_cycle, ANIM_DURATION, ANIM_FPS, final_newline=False) # Ważne: final_newline=False
    entered_key = input() # input() sam przejdzie do nowej linii po Enter
    logging.info(f"Login attempt. Key entered: {'******' if entered_key else 'EMPTY'}")

    if entered_key == correct_key:
        logging.info("Login successful.")
        # Krótki komunikat, który zostanie wyczyszczony
        # final_newline=False, aby nie zostawiać pustej linii przed clear_screen
        print_animated_line(f"{get_time_str()} I ", "Access", " I Granted. Starting...", green_gradient_cycle, ANIM_DURATION, ANIM_FPS, final_newline=False, clear_line_before=True)
        time.sleep(0.5) # Daj czas na przeczytanie
        clear_screen() # Kluczowe: wyczyść ekran PRZED zwróceniem True
        return True
    else:
        logging.warning("Login failed: Incorrect key.")
        # Krótki komunikat, który zostanie wyczyszczony
        print_animated_line(f"{get_time_str()} I ", "Access", " I Denied. Exiting...", red_gradient_cycle, ANIM_DURATION, ANIM_FPS, final_newline=False, clear_line_before=True)
        time.sleep(1) # Daj czas na przeczytanie
        clear_screen() # Kluczowe: wyczyść ekran PRZED zwróceniem False
        return False

# --- Główny skrypt ---
if __name__ == "__main__":
    login_successful = main_login_sequence() # Wynik logowania zapisany do zmiennej

    if not login_successful:
        # Ekran jest już wyczyszczony przez main_login_sequence()
        print("Login failed. Press Enter to exit.") # Prosty komunikat na czystym ekranie
        input()
        logging.info("--- Application Lare Terminated (Login Failed) ---")
        sys.exit()

    # Jeśli logowanie się powiodło, ekran jest już czysty.
    # Teraz można wyświetlić ASCII art "Lare" i kontynuować.
    logging.info("--- Application Lare Started ---")
    project_display_name_input = ""
    author_name_input = ""
    plugin_artifact_id_input = ""

    final_processed_group_id = ""
    final_processed_artifact_id = ""
    final_processed_project_name = ""

    ascii_art_text_lare = """
  ██▓     ▄▄▄         ██▀███  ▓█████
▓██▒    ▒████▄     ▓██ ▒ ██▒▓█   ▀
▒██░    ▒██  ▀█▄   ▓██ ░▄█ ▒▒███  
▒██░    ░██▄▄▄▄██  ▒██▀▀█▄   ▒▓█  ▄
░██████▒▓█    ▓██▒░██▓ ▒██▒░▒████▒
░ ▒░▓   ░▒▒    ▓▒█░░ ▒▓ ░▒▓░░░ ▒░ ░
░ ░ ▒   ░ ▒    ▒▒ ░  ░▒ ░ ▒░ ░ ░  ░
  ░ ░     ░    ▒      ░░   ░    ░   
    ░   ░      ░  ░   ░        ░  ░
""" # Zmieniłem nazwę zmiennej na ascii_art_text_lare dla jasności
    art_start_color = (0, 100, 0); art_end_color = (50, 205, 50)
    if ascii_art_text_lare.startswith('\n'): ascii_art_text_lare = ascii_art_text_lare[1:]
    print_vertical_gradient_text(ascii_art_text_lare, art_start_color, art_end_color)
    print()

    current_time = get_time_str()
    folder_prompt_prefix_text = f"{current_time} I "
    folder_prompt_suffix_text = " I Please provide what name of folder, do you want: "
    print_animated_line(folder_prompt_prefix_text, "Info", folder_prompt_suffix_text, green_gradient_cycle, ANIM_DURATION, ANIM_FPS, final_newline=False, log_message_override="Prompting for folder name.")
    folder_name = input()
    logging.info(f"User entered folder name: '{folder_name}'")

    folder_created = False
    created_folder_path = ""

    if folder_name:
        try:
            os.mkdir(folder_name)
            created_folder_path = os.path.abspath(folder_name)
            folder_created = True
            current_time = get_time_str()
            msg_prefix = f"{current_time} I "; msg_suffix = " I Great! Your starter folder has been created."
            print_animated_line(msg_prefix, "Config", msg_suffix, green_gradient_cycle, ANIM_DURATION, ANIM_FPS, final_newline=True, log_message_override=f"Folder '{created_folder_path}' created successfully.", clear_line_before=True)
        except FileExistsError:
            created_folder_path = os.path.abspath(folder_name)
            current_time = get_time_str()
            msg_prefix = f"{current_time} I "; msg_suffix = " I Sorry, An error occurred. Folder already exists."
            print_animated_line(msg_prefix, "Config", msg_suffix, red_gradient_cycle, ANIM_DURATION, ANIM_FPS, final_newline=True, log_level=logging.WARNING, log_message_override=f"Folder '{created_folder_path}' already exists.", clear_line_before=True)
        except OSError as e:
            current_time = get_time_str()
            msg_prefix = f"{current_time} I "; msg_suffix = f" I Sorry, An error occurred: {e}"
            print_animated_line(msg_prefix, "Config", msg_suffix, red_gradient_cycle, ANIM_DURATION, ANIM_FPS, final_newline=True, log_level=logging.ERROR, log_message_override=f"OSError when creating folder '{folder_name}': {e}", clear_line_before=True)
    else:
        current_time = get_time_str()
        msg_prefix = f"{current_time} I "; msg_suffix = " I No folder name was provided. Starter folder not created."
        print_animated_line(msg_prefix, "Config", msg_suffix, red_gradient_cycle, ANIM_DURATION, ANIM_FPS, final_newline=True, log_level=logging.WARNING, log_message_override="No folder name provided. Folder creation skipped.", clear_line_before=True)

    if folder_name:
        print("\n") # Celowy odstęp, jeśli podano nazwę folderu

    if folder_created:
        current_time = get_time_str()
        pom_info_prompt_prefix = f"{current_time} I "
        pom_name_prompt_suffix = " I Please provide your informations about name: "
        print_animated_line(pom_info_prompt_prefix, "Info", pom_name_prompt_suffix, green_gradient_cycle, ANIM_DURATION, ANIM_FPS, final_newline=False, log_message_override="Prompting for project display name.")
        project_display_name_input = input()
        logging.info(f"User entered project display name: '{project_display_name_input}'")

        current_time = get_time_str()
        pom_info_prompt_prefix = f"{current_time} I "
        pom_author_prompt_suffix = " I Please provide your informations about author: "
        print_animated_line(pom_info_prompt_prefix, "Info", pom_author_prompt_suffix, green_gradient_cycle, ANIM_DURATION, ANIM_FPS, final_newline=False, log_message_override="Prompting for author name.")
        author_name_input = input()
        logging.info(f"User entered author name: '{author_name_input}'")

        current_time = get_time_str()
        pom_info_prompt_prefix = f"{current_time} I "
        pom_plugin_name_prompt_suffix = " I Please provide your informations about plugin name: "
        print_animated_line(pom_info_prompt_prefix, "Info", pom_plugin_name_prompt_suffix, green_gradient_cycle, ANIM_DURATION, ANIM_FPS, final_newline=False, log_message_override="Prompting for plugin artifactId (plugin name).")
        plugin_artifact_id_input = input()
        logging.info(f"User entered plugin artifactId: '{plugin_artifact_id_input}'")

        if project_display_name_input and author_name_input and plugin_artifact_id_input:
            sanitized_author = re.sub(r'[^a-z0-9_.-]', '', author_name_input.lower().replace(" ", "."))
            if not sanitized_author: sanitized_author = "default.author"
            final_processed_group_id = f"pl.{sanitized_author}"

            final_processed_artifact_id = re.sub(r'[^a-zA-Z0-9_.-]', '', plugin_artifact_id_input.replace(" ", "-"))
            if not final_processed_artifact_id: final_processed_artifact_id = "myplugin"

            final_processed_project_name = project_display_name_input
            logging.info(f"Processed POM info: GroupID='{final_processed_group_id}', ArtifactID='{final_processed_artifact_id}', ProjectName='{final_processed_project_name}'")

            pom_xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>{final_processed_group_id}</groupId>
    <artifactId>{final_processed_artifact_id}</artifactId>
    <version>1.0-SNAPSHOT</version>
    <name>{final_processed_project_name}</name>
    <packaging>jar</packaging>
    <properties>
        <java.version>17</java.version>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    <repositories>
        <repository>
            <id>spigotmc-repo</id>
            <url>https://hub.spigotmc.org/nexus/content/repositories/snapshots/</url>
        </repository>
    </repositories>
    <dependencies>
        <dependency>
            <groupId>org.spigotmc</groupId>
            <artifactId>spigot-api</artifactId>
            <version>1.20.1-R0.1-SNAPSHOT</version>
            <scope>provided</scope>
        </dependency>
    </dependencies>
    <build>
        <defaultGoal>clean package</defaultGoal>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
                <configuration>
                    <source>${"{java.version}"}</source>
                    <target>${"{java.version}"}</target>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-shade-plugin</artifactId>
                <version>3.5.1</version>
                <executions>
                    <execution>
                        <phase>package</phase>
                        <goals><goal>shade</goal></goals>
                        <configuration><createDependencyReducedPom>false</createDependencyReducedPom></configuration>
                    </execution>
                </executions>
            </plugin>
        </plugins>
        <resources><resource><directory>src/main/resources</directory><filtering>true</filtering></resource></resources>
    </build>
</project>
"""
            pom_file_full_path = os.path.join(created_folder_path, "pom.xml")
            try:
                write_file_content(pom_file_full_path, pom_xml_template)
                current_time = get_time_str()
                msg_prefix = f"{current_time} I "; msg_suffix = " I Great! Your pom.xml has been created."
                print_animated_line(msg_prefix, "Config", msg_suffix, green_gradient_cycle, ANIM_DURATION, ANIM_FPS, final_newline=True, log_message_override=f"pom.xml created successfully at {pom_file_full_path}", clear_line_before=True)
            except IOError as e:
                current_time = get_time_str()
                msg_prefix = f"{current_time} I "; msg_suffix = f" I Sorry, An error occurred while writing pom.xml: {e}"
                print_animated_line(msg_prefix, "Config", msg_suffix, red_gradient_cycle, ANIM_DURATION, ANIM_FPS, final_newline=True, log_level=logging.ERROR, log_message_override=f"IOError while writing pom.xml: {e}", clear_line_before=True)
        else:
            current_time = get_time_str()
            msg_prefix = f"{current_time} I "; msg_suffix = " I Not all information for pom.xml was provided. File not created."
            print_animated_line(msg_prefix, "Config", msg_suffix, red_gradient_cycle, ANIM_DURATION, ANIM_FPS, final_newline=True, log_level=logging.WARNING, log_message_override="Not all info for pom.xml provided. File not created.", clear_line_before=True)
            final_processed_group_id = ""
            final_processed_artifact_id = ""

        if folder_created and final_processed_group_id and final_processed_artifact_id:
            print("\n") # Celowy odstęp
            current_time = get_time_str()
            caution_prefix_text = f"{current_time} I "
            caution_suffix_text = " I Do you want to proceed starter files? Yes or No: "
            print_animated_line(caution_prefix_text, "Caution", caution_suffix_text, caution_gradient_cycle, ANIM_DURATION, ANIM_FPS, final_newline=False, log_message_override="Prompting user: proceed with starter files (Yes/No)?")
            user_choice_starter_files = input().strip().lower()
            logging.info(f"User choice for starter files: '{user_choice_starter_files}'")

            if user_choice_starter_files == "yes":
                generate_starter_files_and_folders(
                    created_folder_path,
                    final_processed_group_id,
                    final_processed_artifact_id,
                    final_processed_project_name,
                    author_name_input
                )
                current_time = get_time_str()
                done_prefix_text = f"{current_time} I "
                done_suffix_text = " I Great! Your starter plugin folders and files are created."
                print_animated_line(done_prefix_text, "Done", done_suffix_text, done_gradient_cycle, ANIM_DURATION, ANIM_FPS, final_newline=True, log_message_override="Starter plugin folders and files created.", clear_line_before=True)
            elif user_choice_starter_files == "no":
                current_time = get_time_str()
                info_prefix_text = f"{current_time} I "
                info_suffix_text = " I Starter files creation skipped by user."
                print_animated_line(info_prefix_text, "Info", info_suffix_text, green_gradient_cycle, ANIM_DURATION, ANIM_FPS, final_newline=True, log_message_override="Starter files creation skipped by user.", clear_line_before=True)
            else:
                current_time = get_time_str()
                error_prefix_text = f"{current_time} I "
                error_suffix_text = " I Invalid input. Starter files creation skipped."
                print_animated_line(error_prefix_text, "Config", error_suffix_text, red_gradient_cycle, ANIM_DURATION, ANIM_FPS, final_newline=True, log_level=logging.WARNING, log_message_override="Invalid input for starter files prompt. Creation skipped.", clear_line_before=True)
    else:
        logging.info("Skipping POM and starter files generation as base folder was not created or an error occurred.")

    logging.info("--- Application Lare Finished ---")
    # Dodajemy clear_line_before=True, aby upewnić się, że linia jest czysta przed input()
    sys.stdout.write(f"\r\033[K")
    sys.stdout.flush()
    input("\nNaciśnij Enter, aby zakończyć...")