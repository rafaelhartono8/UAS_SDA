import tkinter as tk
import customtkinter as ctk
import json
import os
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv


ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue")  
class TreeNode:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = []
        if parent:
            parent.add_child(self)
    
    def add_child(self, node):
        self.children.append(node)
    
    def remove_child(self, node):
        if node in self.children:
            self.children.remove(node)
            return True
        return False
    
    def to_dict(self):
        return {
            "name": self.name,
            "children": [child.to_dict() for child in self.children]
        }
    
    @classmethod
    def from_dict(cls, data, parent=None):
        node = cls(data["name"], parent)
        for child_data in data["children"]:
            cls.from_dict(child_data, node)
        return node

    def find_node(self, name):
        queue = [self]
        while queue:
            current = queue.pop(0)
            if current.name == name:
                return current
            queue.extend(current.children)
        return None

    def find_path(self, target_node, path=None):
        if path is None:
            path = []
        path.append(self.name)
        if self.name == target_node.name:
            return path
        for child in self.children:
            found_path = child.find_path(target_node, list(path))
            if found_path:
                return found_path
        return None

class App:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Sistem Rekomendasi Makanan")
        self.root.geometry("1200x800")
        self.root.configure(fg_color="#FFFDD0") 
        self.current_user = None
        self.users_file = "users.json"
        self.food_db_file = "food_db.json"
        self.history = []
        
        self.users_data = {}
        self.food_db = None
        
        self.DB_STRUCTURE_NAME = "FNB_Database_Structure"
        self.DB_DUMMY_NAME = "FNB_Database_Dummy"

        self.ALLERGEN_NAMES_SPECIFIC = ["Susu sapi", "Telur", "Seafood", "Kacang", "Gluten"]
        self.ALLERGEN_OPTIONS = self.ALLERGEN_NAMES_SPECIFIC + ["Tanpa Alergen"]

        self.initialize_data_files()
        self.load_data()
        self.create_widgets()

        if not self.food_db:
            messagebox.showwarning("Peringatan Database",
                                f"Database makanan ({self.food_db_file}) tidak dapat dimuat dengan benar atau struktur utama 'Main' tidak ditemukan. " +
                                " Pastikan file JSON ada dan memiliki struktur 'Main' dengan sub-keys " +
                                f"'{self.DB_STRUCTURE_NAME}' dan '{self.DB_DUMMY_NAME}'. Aplikasi mungkin tidak berfungsi dengan benar.") 
        self.show_login()
    
    def visualize_dfs_search(self):
            try:          
                print("Metode visualize_dfs_search dipanggil")
                search_criteria = self.get_search_criteria()
                if not search_criteria:
                    messagebox.showwarning("Peringatan", "Tidak ada kriteria pencarian yang dipilih.")
                    return

                dummy_db_root = None
                if self.food_db:
                    dummy_db_root = self.food_db.find_node(self.DB_DUMMY_NAME)

                if not dummy_db_root:
                    messagebox.showerror("Error", f"Database '{self.DB_DUMMY_NAME}' tidak ditemukan untuk visualisasi DFS.")
                    return

                visited_steps = [] 
                matched_nodes = [] 
                selected_type = search_criteria.get("Jenis Konsumsi")
                selected_category = search_criteria.get("Kategori")
                selected_jenis_makanan = search_criteria.get("Waktu Konsumsi")
                selected_texture = search_criteria.get("Tekstur")
                selected_suhu_minuman = search_criteria.get("Suhu")
                selected_tastes = search_criteria.get("Rasa")
                selected_allergens = search_criteria.get("Alergen")

                def traverse_and_filter_for_viz(node, current_path):
                    print("Memulai traverse_and_filter_for_viz")
                    if not node:
                        return
                    visited_steps.append(node.name)

                    new_criteria_path = current_path + [node.name]
                    path_elements_lower = [p.lower() for p in new_criteria_path]
                    if not node.children:
                        matches_all_criteria = True
                        is_food_path = "makanan berat" in path_elements_lower or "makanan ringan" in path_elements_lower
                        is_drink_path = "minuman" in path_elements_lower

                        if selected_type == "Makanan" and not is_food_path:
                            matches_all_criteria = False
                        elif selected_type == "Minuman" and not is_drink_path:
                            matches_all_criteria = False

                        if matches_all_criteria: 
                            if selected_type == "Makanan":
                                if selected_jenis_makanan and selected_jenis_makanan not in new_criteria_path:
                                    matches_all_criteria = False
                                if selected_category and selected_category not in new_criteria_path:
                                    matches_all_criteria = False
                                if selected_texture and selected_texture.lower() not in path_elements_lower:
                                    matches_all_criteria = False
                                if selected_tastes and not any(taste.lower() in path_elements_lower for taste in selected_tastes):
                                        matches_all_criteria = False
                                if "Tanpa Alergen" in selected_allergens:
                                    for allergen_option in self.ALLERGEN_NAMES_SPECIFIC:
                                        if allergen_option.lower() in path_elements_lower:
                                            matches_all_criteria = False
                                            break
                                else:
                                    found_specific_allergen = False
                                    for allergen_option in selected_allergens:
                                        if allergen_option.lower() in path_elements_lower:
                                            found_specific_allergen = True
                                            break
                                    if not found_specific_allergen:
                                        matches_all_criteria = False

                            elif selected_type == "Minuman":
                                if selected_suhu_minuman and selected_suhu_minuman.lower() not in path_elements_lower:
                                    matches_all_criteria = False
                                if selected_tastes and not any(taste.lower() in path_elements_lower for taste in selected_tastes):
                                    matches_all_criteria = False
                                if "Tanpa Alergen" in selected_allergens:
                                    for allergen_option in self.ALLERGEN_NAMES_SPECIFIC:
                                        if allergen_option.lower() in path_elements_lower:
                                            matches_all_criteria = False
                                            break
                                else:
                                    found_specific_allergen = False
                                    for allergen_option in selected_allergens:
                                        if allergen_option.lower() in path_elements_lower:
                                            found_specific_allergen = True
                                            break
                                    if not found_specific_allergen:
                                        matches_all_criteria = False

                        if matches_all_criteria:
                            matched_nodes.append(node.name) 
                        return 
                    print("Selesai traverse_and_filter_for_viz")

                    for child in node.children:
                        traverse_and_filter_for_viz(child, new_criteria_path)
                if selected_type == "Makanan":
                    print("selesai traverse_and_filter_for_viz")
                    start_nodes = [dummy_db_root.find_node("Makanan Berat"), dummy_db_root.find_node("Makanan Ringan")]
                    for node in start_nodes:
                        if node:
                            traverse_and_filter_for_viz(node, [])
                elif selected_type == "Minuman":
                    print("selesai traverse_and_filter_for_viz")
                    start_node = dummy_db_root.find_node("Minuman")
                    if start_node:
                        traverse_and_filter_for_viz(start_node, [])
                DFSSearchVisualizationWindow(self.root, dummy_db_root, visited_steps, matched_nodes, f"Visualisasi DFS: {self.format_search_query(search_criteria)}")
            except Exception as e:
                print (f"Kesalahan terjadi: {e}")

    def initialize_data_files(self):
        if not os.path.exists(self.users_file):
            with open(self.users_file, "w") as f:
                json.dump({}, f) 
        if not os.path.exists(self.food_db_file):
            with open(self.food_db_file, "w") as f:
                json.dump({"Main": {self.DB_STRUCTURE_NAME: {}, self.DB_DUMMY_NAME: {}}}, f, indent=2)

    def _parse_new_json_structure(self, current_data, parent_node):
        if isinstance(current_data, dict):
            for name, children_data in current_data.items():
                node = TreeNode(name, parent_node)
                self._parse_new_json_structure(children_data, node)
        elif isinstance(current_data, list): 
            for item_name in current_data:
                if isinstance(item_name, str):
                    TreeNode(item_name, parent_node) 
    
    def load_data(self):
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, "r", encoding="utf-8") as f:
                    self.users_data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showerror("Error", f"Gagal memuat data pengguna: {e}")
                self.users_data = {}
        
        if os.path.exists(self.food_db_file):
            try:
                with open(self.food_db_file, "r", encoding="utf-8") as f:
                    data_from_file = json.load(f)
                if data_from_file:
                    if isinstance(data_from_file, dict) and data_from_file.get("name") == "Main":
                        self.food_db = TreeNode.from_dict(data_from_file)
                    elif isinstance(data_from_file, dict) and "Main" in data_from_file and isinstance(data_from_file["Main"], dict):
                        self.food_db = TreeNode("Main")
                        self._parse_new_json_structure(data_from_file["Main"], self.food_db)
                    else:
                        self.food_db = None
                        messagebox.showwarning("Format Error", f"Format {self.food_db_file} tidak valid. Root 'Main' tidak ditemukan atau struktur internal salah.")
                else: 
                    self.food_db = None
            except (json.JSONDecodeError, IOError, AttributeError, TypeError, ValueError) as e:
                messagebox.showerror("Error", f"Gagal memuat database makanan: {e}")
                self.food_db = None

        else: 
                self.food_db = None
        should_initialize_full_db = False
        if not self.food_db:
            should_initialize_full_db = True
        else:
            structure_node = self.food_db.find_node(self.DB_STRUCTURE_NAME)
            dummy_node = self.food_db.find_node(self.DB_DUMMY_NAME)
            if not structure_node or not dummy_node or (structure_node and not structure_node.children) or(dummy_node and not dummy_node.children):
                should_initialize_full_db = True
        
        if should_initialize_full_db:
            messagebox.showinfo("Info Database", f"Database makanan ({self.food_db_file}) tidak ada, kosong, atau strukturnya minimal. Menginisialisasi dengan data default.")
            self.initialize_food_database()
    
    def save_data(self):
        try:
            with open(self.users_file, "w") as f:
                json.dump(self.users_data, f, indent=4)
        except IOError as e:
            messagebox.showerror("Error", f"Gagal menyimpan data pengguna: {e}")
   
        if self.food_db:
            try:
                with open(self.food_db_file, "w") as f:
                    json.dump(self.food_db.to_dict(), f, indent=4)
            except IOError as e:
                messagebox.showerror("Error", f"Gagal menyimpan database makanan: {e}")

    def initialize_food_database(self):
        self.food_db = TreeNode("Main") 
        food_structure_node = TreeNode(self.DB_STRUCTURE_NAME, self.food_db)
        makanan_berat_node = TreeNode("Makanan Berat", food_structure_node)
        makanan_ringan_node = TreeNode("Makanan Ringan", food_structure_node)
        minuman_node = TreeNode("Minuman", food_structure_node)
        categories = ["Bebas", "Tanpa Sayur", "Vegetarian", "Vegan"]
        textures = ["Kering", "Berkuah"]
        tastes_food = ["Manis", "Asin/Gurih", "Asam", "Pahit", "Pedas"] 
        allergens = ["Mengandung Susu Sapi", "Mengandung Telur", "Mengandung Seafood", "Mengandung Kacang", "Mengandung Gluten", "Tanpa Alergen"]

        for parent_node in [makanan_berat_node, makanan_ringan_node]:
            for category in categories:
                category_node = TreeNode(category, parent_node)
                for texture in textures:
                    texture_node = TreeNode(texture, category_node)
                    for taste in tastes_food:
                        taste_node = TreeNode(taste, texture_node)
                        for allergen in allergens:
                            TreeNode(allergen, taste_node) 
        suhu_node_minuman = TreeNode("Suhu", minuman_node)
        panas_node_minuman = TreeNode("Panas", suhu_node_minuman)
        dingin_node_minuman = TreeNode("Dingin", suhu_node_minuman)

        tastes_minuman = ["Manis", "Asin", "Asam", "Pahit", "Pedas"] 

        for parent_node_minuman in [panas_node_minuman, dingin_node_minuman]:
            for taste_minuman in tastes_minuman:
                taste_node_minuman = TreeNode(taste_minuman, parent_node_minuman)
                for allergen in allergens:
                    TreeNode(allergen, taste_node_minuman) 
        self.create_dummy_database() 
        self.save_data() 
        
    def create_dummy_database(self):
        dummy_db_node = self.food_db.find_node(self.DB_DUMMY_NAME)

        if dummy_db_node:
            dummy_db_node.children.clear() 
        else:
            dummy_db_node = TreeNode(self.DB_DUMMY_NAME, self.food_db)
        dummy_data = {
            "Makanan Berat": {
                "Bebas": {
                    "Kering": {
                        "Manis": ["Nasi Kuning Komplit", "Nasi Uduk Manis", "Mie Goreng Manis", "Ayam Bakar Madu", "Sate Lilit Manis"],
                        "Asin/Gurih": ["Nasi Padang", "Nasi Goreng Seafood", "Sate Ayam Madura", "Rendang Sapi", "Gudeg Komplit"],
                        "Asam": ["Ayam Asam Manis", "Ikan Asam Pedas", "Tumis Kangkung Asam", "Gurame Bakar Asam", "Nasi Tim Ayam Asam"],
                        "Pahit": ["Nasi Pepes Pare", "Tumis Pare Udang", "Sayur Pahit Tempe", "Gado-gado Pare", "Botok Pare"],
                        "Pedas": ["Ayam Geprek", "Nasi Goreng Pedas Gila", "Seblak Ceker", "Rica-rica Ayam", "Balado Terong"]
                    },
                    "Berkuah": {
                        "Manis": ["Bubur Sumsum Candil", "Kolak Pisang Ubi"], 
                        "Asin/Gurih": ["Soto Ayam Lamongan", "Rawon", "Bakso Kuah", "Sop Buntut", "Coto Makassar"],
                        "Asam": ["Sayur Asem", "Pindang Ikan Patin", "Garang Asem Ayam", "Sop Ikan Asam Pedas"],
                        "Pahit": ["Sayur Pahit Berkuah", "Brongkos"], 
                        "Pedas": ["Sayur Lodeh Pedas", "Gulai Ayam Pedas", "Sop Iga Pedas", "Mie Kuah Pedas", "Tom Yam Seafood"]
                    }
                },
                "Tanpa Sayur": {
                     "Kering": {
                        "Manis": ["Ayam Bakar Madu (polos)", "Sate Manis (polos)", "Ikan Bakar Kecap (polos)", "Tahu Tempe Bacem", "Dendeng Manis"],
                        "Asin/Gurih": ["Ayam Goreng Lengkuas", "Ikan Goreng Kremes", "Telur Balado Polos", "Sapi Lada Hitam (tanpa paprika)", "Paru Goreng"],
                        "Asam": ["Ayam Goreng Asam Manis (polos)", "Ikan Asam Manis (polos)"], 
                        "Pahit": [], 
                        "Pedas": ["Ayam Geprek Polos", "Bebek Goreng Pedas", "Sambal Goreng Kentang (tanpa hati)"]
                    },
                    "Berkuah": {
                        "Manis": ["Bubur Kacang Hijau (polos)", "Kolak Pisang (polos)"],
                        "Asin/Gurih": ["Soto Daging Bening (polos)", "Bakso Urat (polos)", "Sup Ayam Bening (polos)", "Rawon Daging (polos)", "Kuah Bakso Polos"],
                        "Asam": [], 
                        "Pahit": [], 
                        "Pedas": ["Kuah Bakso Pedas Polos", "Sop Iga Pedas (polos)"]
                    }
                },
                "Vegetarian": { 
                     "Kering": {
                        "Manis": ["Terong Balado Manis (telur)", "Tahu Kecap Manis", "Tempe Goreng Tepung Manis", "Lumpia Semarang (sayur, telur)", "Martabak Manis (telur, susu)"],
                        "Asin/Gurih": ["Tempe Orek Kering", "Tahu Goreng Bumbu", "Telur Dadar Crispy", "Perkedel Kentang", "Jamur Crispy"],
                        "Asam": ["Asinan Buah", "Rujak Cingur (tahu/tempe)", "Tumis Jamur Asam"],
                        "Pahit": ["Tumis Pare Tahu", "Pecel Pare"],
                        "Pedas": ["Tahu Gejrot", "Tempe Penyet", "Terong Balado", "Pete Goreng Sambal", "Kentang Mustofa Pedas"]
                    },
                    "Berkuah": {
                        "Manis": ["Bubur Sumsum", "Kolak Singkong"],
                        "Asin/Gurih": ["Sayur Lodeh", "Gulai Nangka (vegetarian)", "Sop Tahu", "Bakwan Kuah"],
                        "Asam": ["Sayur Asem (vegetarian)", "Sop Buah Asam"],
                        "Pahit": ["Sayur Lodeh Pare", "Bobor Daun Katuk"],
                        "Pedas": ["Sayur Lodeh Pedas", "Gulai Nangka Pedas", "Sambal Tumpang"]
                    }
                },
                "Vegan": { 
                     "Kering": {
                        "Manis": ["Misro", "Onde-onde", "Gemblong", "Getuk", "Klepon"],
                        "Asin/Gurih": ["Tahu Crispy", "Tempe Mendoan (vegan)", "Perkedel Kentang (vegan)", "Cireng (vegan)", "Singkong Goreng"],
                        "Asam": ["Asinan Sayur", "Rujak Buah"],
                        "Pahit": ["Tumis Pare"],
                        "Pedas": ["Tahu Mercon", "Cimol Pedas (vegan)", "Kerupuk Pedas"]
                    },
                    "Berkuah": {
                         "Manis": ["Bubur Ketan Hitam (santan nabati)", "Kolak Ubi (santan nabati)"],
                        "Asin/Gurih": ["Sup Tahu Putih (kuah bening)", "Cilok Kuah Bening", "Sayur Asem (vegan)", "Lodeh Labu Siam", "Gulai Nangka (santan nabati)"],
                        "Asam": ["Sayur Asam Kangkung", "Tomat Sayur Asam"],
                        "Pahit": ["Sayur Pare Kuah"],
                        "Pedas": ["Seblak Vegan (tanpa kerupuk hewani)", "Sayur Lodeh Pedas (santan nabati)", "Gulai Nangka Pedas (santan nabati)"]
                    }
                }
            },
            "Makanan Ringan": {
                "Bebas": {
                    "Kering": {
                        "Manis": ["Kue Kering Nastar", "Kue Cubit Manis", "Donat Gula", "Pisang Cokelat", "Martabak Mini Manis"],
                        "Asin/Gurih": ["Keripik Kentang Asin", "Cireng", "Batagor Kering", "Emping Melinjo", "Kacang Bawang"],
                        "Asam": ["Asinan Bogor (ringan)", "Rujak Serut", "Manisan Buah Asam"],
                        "Pahit": ["Keripik Pare"],
                        "Pedas": ["Basreng Pedas", "Makaroni Pedas", "Cimol Pedas", "Kerupuk Seblak", "Tahu Pedas"]
                    },
                    "Berkuah": {
                        "Manis": ["Bubur Kacang Ijo", "Kolak Candil"], 
                        "Asin/Gurih": ["Cilok Kuah", "Pempek Kapal Selam", "Batagor Kuah", "Siomay Kuah", "Tekwan"],
                        "Asam": ["Asinan Sayur (berkuah)", "Pempek Lenjer (kuah cuko asam)"],
                        "Pahit": [], 
                        "Pedas": ["Seblak Kuah", "Mie Ayam Pedas", "Baso Aci", "Cilok Goang", "Mie Instan Kuah Pedas"]
                    }
                },
                "Tanpa Sayur": {
                    "Kering": {
                        "Manis": ["Donat Gula", "Kue Putu", "Pisang Goreng Cokelat", "Martabak Mini Manis (polos)", "Kue Pancong"],
                        "Asin/Gurih": ["Cireng Goreng", "Pempek Adaan", "Sosis Solo", "Risoles Ragout (polos)", "Tahu Isi (polos)"],
                        "Asam": ["Kerupuk Ikan Asam"], 
                        "Pahit": [],
                        "Pedas": ["Cimol Goreng Pedas", "Basreng Pedas Kering"]
                    },
                    "Berkuah": {
                        "Manis": ["Bubur Ketan Hitam", "Kolak Pisang"],
                        "Asin/Gurih": ["Bakso Kuah Polos", "Cilok Kuah Polos"],
                        "Asam": [],
                        "Pahit": [],
                        "Pedas": ["Cilok Goang Polos"]
                    }
                },
                "Vegetarian": {
                    "Kering": {
                        "Manis": ["Kue Ape", "Kue Balok", "Kue Cucur", "Getuk Lindri", "Klepon"],
                        "Asin/Gurih": ["Tempe Mendoan", "Tahu Isi Sayur", "Perkedel Jagung", "Lumpia Sayur", "Combro"],
                        "Asam": ["Rujak Cireng"],
                        "Pahit": [],
                        "Pedas": ["Gehu Pedas", "Tahu Hot Jeletot", "Tempe Goreng Tepung Pedas"]
                    },
                    "Berkuah": {
                        "Manis": ["Bubur Sumsum", "Kolak Singkong"],
                        "Asin/Gurih": ["Siomay Kuah (sayuran, tahu)", "Batagor Kuah (tahu, sayuran)"],
                        "Asam": ["Asinan Betawi (sayuran)"],
                        "Pahit": [],
                        "Pedas": ["Seblak Jeletot (sayuran)"]
                    }
                },
                "Vegan": {
                     "Kering": {
                        "Manis": ["Misro", "Onde-onde", "Gemblong", "Getuk", "Klepon"],
                        "Asin/Gurih": ["Tahu Crispy", "Tempe Mendoan (adonan tanpa telur)", "Perkedel Kentang (tanpa telur)", "Cireng (tanpa telur)", "Singkong Goreng"],
                        "Asam": ["Asinan Buah (tanpa terasi)"],
                        "Pahit": [],
                        "Pedas": ["Tahu Mercon", "Cimol Pedas (vegan)", "Kerupuk Pedas"]
                    },
                    "Berkuah": {
                         "Manis": ["Bubur Ketan Hitam (santan nabati)", "Kolak Ubi (santan nabati)"],
                        "Asin/Gurih": ["Sup Tahu Putih (kuah bening)", "Cilok Kuah Bening", "Asinan Sayur (kuah asam vegan)"],
                        "Asam": ["Asinan Sayur (kuah asam vegan)"],
                        "Pahit": [],
                        "Pedas": ["Seblak Vegan (tanpa kerupuk hewani)"]
                    }
                }
            },
            "Minuman": {
                "Suhu": {
                    "Panas": {
                        "Manis": ["Teh Manis Panas", "Kopi Susu Panas", "Cokelat Panas", "Wedang Jahe", "Bajigur"],
                        "Asin": ["Wedang Jahe Asin", "Air Garam Hangat"], 
                        "Asam": ["Asam Jawa Panas", "Wedang Uwuh (rasa asam sedikit)"],
                        "Pahit": ["Kopi Hitam", "Teh Pahit", "Wedang Serbat", "Jamu Kunyit Asam", "Jamu Beras Kencur"], 
                        "Pedas": ["Wedang Ronde (pedas jahe)", "Wedang Jahe Susu (dengan jahe pedas)"]
                    },
                    "Dingin": {
                        "Manis": ["Es Teh Manis", "Es Kopi Susu", "Es Cokelat", "Es Dawet", "Es Buah", "Es Teler", "Es Campur", "Es Cendol", "Es Pisang Ijo", "Es Selendang Mayang"], 
                        "Asin": ["Es Cincau Asin", "Minuman Isotonik Asin"], 
                        "Asam": ["Es Jeruk", "Es Limun", "Es Asam Jawa", "Es Kuwut"],
                        "Pahit": ["Es Kopi Hitam", "Es Teh Pahit"],
                        "Pedas": ["Es Cincau Pedas", "Es Degan Pedas"]
                    }
                }
            }
        }
     
        food_allergens_map = {
            "Mengandung Susu Sapi": ["Martabak Manis", "Kopi Susu Panas", "Es Kopi Susu", "Cokelat Panas", "Es Cokelat", "Kue Sus", "Es Krim"],
            "Mengandung Telur": ["Martabak Manis", "Kue Bolu", "Telur Dadar Polos", "Semar Mendem", "Ayam Goreng Tepung", "Lumpia Semarang (sayur, telur)"],
            "Mengandung Seafood": ["Nasi Goreng Seafood", "Tom Yum Seafood", "Udang Balado", "Cumi Saus Padang", "Pempek Kapal Selam", "Pempek Lenjer (kuah cuko asam)", "Tekwan"],
            "Mengandung Kacang": ["Gado-gado Komplit", "Sate Ayam Madura", "Pecel Pare", "Ketoprak", "Martabak Manis (topping kacang)", "Kacang Bawang"],
            "Mengandung Gluten": ["Mie Goreng Manis", "Mie Kuah Pedas", "Mie Instan Kuah Pedas", "Roti Bakar", "Kue Bolu", "Martabak", "Gorengan", "Cireng", "Basreng Pedas", "Makaroni Pedas", "Cimol Pedas", "Kerupuk Seblak"]
        }
        
        def add_dummy_nodes_recursively(parent_node_obj, data_dict_or_list):
            if isinstance(data_dict_or_list, dict):
                for key, value in data_dict_or_list.items():
                    current_node_obj = TreeNode(key, parent_node_obj)
                    add_dummy_nodes_recursively(current_node_obj, value)
            elif isinstance(data_dict_or_list, list):
                all_possible_allergens = ["Mengandung Susu Sapi", "Mengandung Telur", "Mengandung Seafood", "Mengandung Kacang", "Mengandung Gluten", "Tanpa Alergen"]
                allergen_nodes_map = {}
                for allergen_type in all_possible_allergens:
                    allergen_nodes_map[allergen_type] = TreeNode(allergen_type, parent_node_obj)

                for item_name in data_dict_or_list:
                    item_added_to_allergen = False
                    for allergen_type, foods_with_allergen in food_allergens_map.items():
                        if item_name in foods_with_allergen:
                            TreeNode(item_name, allergen_nodes_map[allergen_type])
                            item_added_to_allergen = True
                            
                    if not item_added_to_allergen:
                        TreeNode(item_name, allergen_nodes_map["Tanpa Alergen"])

        for top_level_name, top_level_data in dummy_data.items():
            top_level_node = TreeNode(top_level_name, dummy_db_node)
            add_dummy_nodes_recursively(top_level_node, top_level_data)

    def create_widgets(self):
        self.login_frame = ctk.CTkFrame(self.root, fg_color="#FFFDD0")
        self.register_frame = ctk.CTkFrame(self.root, fg_color="#FFFDD0")
        self.quiz_frame = ctk.CTkFrame(self.root, fg_color="#FFFDD0")
        self.main_menu_frame = ctk.CTkFrame(self.root, fg_color="#FFFDD0")
        self.database_frame = ctk.CTkFrame(self.root, fg_color="#FFFDD0")
        self.search_frame = ctk.CTkFrame(self.root, fg_color="#FFFDD0")
        self.history_frame = ctk.CTkFrame(self.root, fg_color="#FFFDD0")
        self.profile_frame = ctk.CTkFrame(self.root, fg_color="#FFFDD0")
        
        self.setup_login_widgets()
  
        self.setup_register_widgets()
   
        self.setup_quiz_widgets()
  
        self.setup_main_menu_widgets()

        self.setup_database_widgets()

        self.setup_search_widgets()

        self.setup_history_widgets()
        
        self.setup_profile_widgets()
    
    def setup_login_widgets(self):
        for widget in self.login_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.login_frame,
            text="SELAMAT DATANG\nMAU MAKAN APA HARI INI?",
            font=("Kanit", 24, "bold"),
            text_color="#424242",
            justify="center"
        ).place(relx=0.5, rely=0.15, anchor="center")

        image_path = "smile.png"
        if os.path.exists(image_path):
            from PIL import Image, ImageTk
            img = Image.open(image_path).resize((180, 180))
            photo = ImageTk.PhotoImage(img)
            img_label = ctk.CTkLabel(self.login_frame, text="", image=photo, fg_color="transparent")
            img_label.image = photo
            img_label.place(relx=0.5, rely=0.35, anchor="center")

        login_box = ctk.CTkFrame(self.login_frame, fg_color="#C16C6C", corner_radius=20)
        login_box.place(relx=0.5, rely=0.6, anchor="center")

        ctk.CTkLabel(login_box, text="LOGIN", font=("Kanit", 18, "bold"), text_color="#1f1f1f").pack(pady=(10, 5))

        self.username_entry = ctk.CTkEntry(login_box, placeholder_text="Username", width=250)
        self.username_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(login_box, placeholder_text="Password", show="*", width=250)
        self.password_entry.pack(pady=5)

        ctk.CTkButton(
            login_box, text="MASUK", fg_color="yellow", text_color="black",
            hover_color="#FFD700", width=200, height=35, font=("Kanit", 14, "bold"),
            command=self.login
        ).pack(pady=(10, 5))

        daftar_frame = ctk.CTkFrame(login_box, fg_color="transparent")
        daftar_frame.pack(pady=(0, 10))

        ctk.CTkLabel(daftar_frame, text="Belum punya akun?", font=("Kanit", 12), text_color="#424242").pack(side="left")
        label_daftar = ctk.CTkLabel(daftar_frame, text=" Daftar", font=("Kanit", 12, "bold"), text_color="yellow", cursor="hand2")
        label_daftar.pack(side="left")
        label_daftar.bind("<Enter>", lambda e: label_daftar.configure(text_color="red"))
        label_daftar.bind("<Leave>", lambda e: label_daftar.configure(text_color="yellow"))
        label_daftar.bind("<Button-1>", lambda e: self.show_register())

    def setup_register_widgets(self):
        for widget in self.register_frame.winfo_children():
            widget.destroy()

        back_label = ctk.CTkLabel(self.register_frame, text="← REGISTRASI", font=("Kanit", 18, "bold"), text_color="#424242", cursor="hand2")
        back_label.place(x=20, y=20)
        back_label.bind("<Button-1>", lambda e: self.show_login())

        ctk.CTkLabel(self.register_frame, text="Selamat Datang!", font=("Kanit", 20, "bold"), text_color="#1f1f1f").place(relx=0.1, rely=0.15, anchor="w")
        ctk.CTkLabel(self.register_frame, text="Registrasi akun kamu untuk mulai mencari rekomendasi makanan.", font=("Kanit", 14), text_color="#1f1f1f").place(relx=0.1, rely=0.21, anchor="w")

        self.new_username_entry = ctk.CTkEntry(self.register_frame, placeholder_text="Username", width=300)
        self.new_username_entry.place(relx=0.1, rely=0.3, anchor="w")

        self.new_password_entry = ctk.CTkEntry(self.register_frame, placeholder_text="Password", show="*", width=300)
        self.new_password_entry.place(relx=0.1, rely=0.37, anchor="w")

        self.confirm_password_entry = ctk.CTkEntry(self.register_frame, placeholder_text="Konfirmasi Password", show="*", width=300)
        self.confirm_password_entry.place(relx=0.1, rely=0.44, anchor="w")

        ctk.CTkButton(
            self.register_frame, text="SELANJUTNYA",
            fg_color="#C16C6C", hover_color="#B04C4C",
            text_color="white", corner_radius=10,
            width=200, height=40,
            font=("Kanit", 14, "bold"),
            command=self.register
        ).place(relx=0.1, rely=0.55, anchor="w")

    # Tambahkan opsi kembali ke login (mobile friendly)
        ctk.CTkLabel(
            self.register_frame,
            text="Sudah punya akun?",
            font=("Kanit", 12),
            text_color="#424242"
        ).place(relx=0.1, rely=0.63, anchor="w")

        kembali_login = ctk.CTkLabel(
            self.register_frame,
            text="Login di sini",
            font=("Kanit", 12, "bold"),
            text_color="yellow",
            cursor="hand2"
        )
        kembali_login.place(relx=0.32, rely=0.63, anchor="w")
        kembali_login.bind("<Enter>", lambda e: kembali_login.configure(text_color="red"))
        kembali_login.bind("<Leave>", lambda e: kembali_login.configure(text_color="yellow"))
        kembali_login.bind("<Button-1>", lambda e: self.show_login())
    
    def setup_quiz_widgets(self):
        ctk.CTkLabel(self.quiz_frame, text="Preferensi Makanan", font=("Arial", 24), text_color="#333333").pack(pady=20)
        
        ctk.CTkLabel(self.quiz_frame, text="Pilih kategori makanan:", text_color="#333333").pack(pady=10)
        self.category_var = ctk.StringVar(value="Bebas")
        for category in ["Bebas", "Tanpa Sayur", "Vegetarian", "Vegan"]:
            ctk.CTkRadioButton(
                self.quiz_frame, 
                text=category, 
                variable=self.category_var, 
                value=category,
                text_color="#333333",
                fg_color="#4CAF50"
            ).pack(pady=2, anchor="w", padx=20)
 
        ctk.CTkLabel(self.quiz_frame, text="Pilih alergi (bisa lebih dari satu):", text_color="#333333").pack(pady=10)
        self.allergy_vars = {}
        for allergy in self.ALLERGEN_OPTIONS:
            var = ctk.BooleanVar()
            ctk.CTkCheckBox(
                self.quiz_frame, 
                text=allergy, 
                variable=var,
                text_color="#333333",
                fg_color="#4CAF50"
            ).pack(pady=2, anchor="w", padx=20)
            self.allergy_vars[allergy] = var
        
        ctk.CTkButton(self.quiz_frame, text="Simpan", command=self.submit_quiz, fg_color="#4CAF50", hover_color="#45a049").pack(pady=20)
    
    def setup_main_menu_widgets(self):
        self.main_menu_label = ctk.CTkLabel(self.main_menu_frame, text="", font=("Arial", 24), text_color="#333333")
        self.main_menu_label.pack(pady=20)
        
        button_frame = ctk.CTkFrame(self.main_menu_frame, fg_color="transparent")
        button_frame.pack(pady=10, padx=10, fill="both", expand=True)
  
        ctk.CTkButton(
            button_frame, 
            text="Database Makanan", 
            command=self.show_database,
            height=40,
            font=("Arial", 14),
            fg_color="#007BFF",
            hover_color="#0056b3"
        ).grid(row=0, column=0, pady=10, padx=10, sticky="nsew")
        
        ctk.CTkButton(
            button_frame, 
            text="Pencarian Makanan", 
            command=self.show_search,
            height=40,
            font=("Arial", 14),
            fg_color="#007BFF",
            hover_color="#0056b3"
        ).grid(row=0, column=1, pady=10, padx=10, sticky="nsew")
        
        ctk.CTkButton(
            button_frame, 
            text="Riwayat Pencarian", 
            command=self.show_history,
            height=40,
            font=("Arial", 14),
            fg_color="#007BFF",
            hover_color="#0056b3"
        ).grid(row=1, column=0, pady=10, padx=10, sticky="nsew")
        
        ctk.CTkButton(
            button_frame, 
            text="Profil Saya", 
            command=self.show_profile,
            height=40,
            font=("Arial", 14),
            fg_color="#007BFF",
            hover_color="#0056b3"
        ).grid(row=1, column=1, pady=10, padx=10, sticky="nsew")
        
        ctk.CTkButton(
            button_frame, 
            text="Logout", 
            command=self.logout,
            height=40,
            font=("Arial", 14),
            fg_color="#d64545",
            hover_color="#b03a3a"
        ).grid(row=2, column=0, columnspan=2, pady=20, sticky="nsew")
 
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)
        button_frame.grid_rowconfigure(2, weight=1)
    
    def setup_database_widgets(self):
        self.tree_frame = ctk.CTkFrame(self.database_frame, fg_color="transparent")
        self.tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
            background="#F5F5DC", 
            foreground="#333333", 
            fieldbackground="#F5F5DC",
            borderwidth=1,
            relief="solid",
            rowheight=25) 
        style.map('Treeview', background=[('selected', '#A9D0F5')]) 
        style.configure("Treeview.Heading",
            background="#007BFF", 
            foreground="white",
            relief="flat",
            font=('Arial', 10, 'bold'))
        style.map("Treeview.Heading",
            background=[('active', '#0056b3')])
        
        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(fill="both", expand=True)
      
        scrollbar_y = ctk.CTkScrollbar(self.tree_frame, orientation="vertical", command=self.tree.yview)
        scrollbar_y.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_x = ctk.CTkScrollbar(self.tree_frame, orientation="horizontal", command=self.tree.xview)
        scrollbar_x.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=scrollbar_x.set)
    
        button_frame = ctk.CTkFrame(self.database_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        ctk.CTkButton(button_frame, text="Tambah Node", command=self.add_node, fg_color="#28a745", hover_color="#218838").grid(row=0, column=0, padx=5)
        ctk.CTkButton(button_frame, text="Edit Node", command=self.edit_node, fg_color="#ffc107", hover_color="#e0a800").grid(row=0, column=1, padx=5)
        ctk.CTkButton(button_frame, text="Tambah Parent", command=self.add_parent, fg_color="#17a2b8", hover_color="#138496").grid(row=0, column=2, padx=5)
        ctk.CTkButton(button_frame, text="Hapus Node", command=self.delete_node, fg_color="#dc3545", hover_color="#c82333").grid(row=0, column=3, padx=5)
        
        ctk.CTkButton(button_frame, text="Visualisasi Tree", command=self.visualize_tree, fg_color="#6f42c1", hover_color="#5a38a1",width=290).grid(row=1, column=0, pady=5, columnspan=2)
        ctk.CTkButton(button_frame, text="Simpan Database", command=self.save_data, fg_color="#007BFF", hover_color="#0056b3").grid(row=1, column=2, pady=5) # Tombol simpan database
        ctk.CTkButton(button_frame, text="Refresh", command=self.refresh_tree, fg_color="#6c757d", hover_color="#5a6268").grid(row=1, column=3, pady=5)
        ctk.CTkButton(button_frame, text="Kembali", command=self.show_main_menu, fg_color="#dc3545", hover_color="#c82333").grid(row=2, column=0, columnspan=4, pady=5)
    
    def perform_search(self):
        search_type = self.search_consumption_type_var.get()
        root_db_node = None
        if self.food_db:
            root_db_node = self.food_db.find_node(self.DB_DUMMY_NAME)
        else:
            messagebox.showerror("Error", "Database makanan belum dimuat.")
            return
        if not root_db_node:
            self.results_text.delete("1.0", "end")
            self.results_text.insert("end", f"Database '{self.DB_DUMMY_NAME}' tidak ditemukan.")
            return 

        results = []
        search_criteria = self.get_search_criteria()
        search_query_str = self.format_search_query(search_criteria)

        selected_category = search_criteria.get("Kategori") 
        selected_jenis_makanan = search_criteria.get("Waktu Konsumsi") 
        selected_texture = search_criteria.get("Tekstur") 
        selected_suhu_minuman = search_criteria.get("Suhu") 
        selected_tastes = search_criteria.get("Rasa")
        selected_allergens = search_criteria.get("Alergen")

        def traverse_and_filter(node, current_criteria_path):
            if not node:
                return

            new_criteria_path = current_criteria_path + [node.name]
            path_elements_lower = [p.lower() for p in new_criteria_path]

            if not node.children:
                matches_all_criteria = True
                if search_type == "Makanan" and "Makanan Berat" not in new_criteria_path and "Makanan Ringan" not in new_criteria_path:
                    matches_all_criteria = False
                elif search_type == "Minuman" and "Minuman" not in new_criteria_path:
                    matches_all_criteria = False
                
                if matches_all_criteria and search_type == "Makanan":
                    if selected_jenis_makanan and selected_jenis_makanan not in new_criteria_path:
                        matches_all_criteria = False
                    if selected_category and selected_category not in new_criteria_path:
                        matches_all_criteria = False
                    if selected_texture and selected_texture.lower() not in path_elements_lower:
                        matches_all_criteria = False
                    if selected_tastes and not any(taste.lower() in path_elements_lower for taste in selected_tastes):
                            matches_all_criteria = False
                    if "Tanpa Alergen" in selected_allergens:
                        for allergen_option in self.ALLERGEN_NAMES_SPECIFIC: 
                            if allergen_option.lower() in path_elements_lower:
                                matches_all_criteria = False
                                break
                    else:
                        found_specific_allergen = False
                        for allergen_option in selected_allergens: 
                            if allergen_option.lower() in path_elements_lower:
                                found_specific_allergen = True
                                break
                        if not found_specific_allergen:
                            matches_all_criteria = False
                
                if matches_all_criteria and search_type == "Minuman":
                    if selected_suhu_minuman and selected_suhu_minuman.lower() not in path_elements_lower:
                        matches_all_criteria = False
                    if selected_tastes and not any(taste.lower() in path_elements_lower for taste in selected_tastes):
                        matches_all_criteria = False
                    if "Tanpa Alergen" in selected_allergens:
                        for allergen_option in self.ALLERGEN_NAMES_SPECIFIC:
                            if allergen_option.lower() in path_elements_lower:
                                matches_all_criteria = False
                                break
                    else:
                        found_specific_allergen = False
                        for allergen_option in selected_allergens:
                            if allergen_option.lower() in path_elements_lower:
                                found_specific_allergen = True
                                break
                        if not found_specific_allergen:
                            matches_all_criteria = False

                if matches_all_criteria:
                    results.append(node.name)
                return

            for child in node.children:
                traverse_and_filter(child, new_criteria_path)

        if search_type == "Makanan":
            start_nodes = [root_db_node.find_node("Makanan Berat"), root_db_node.find_node("Makanan Ringan")] 
            for node in start_nodes:
                if node:
                    traverse_and_filter(node, [])
        elif search_type == "Minuman":
            start_node = root_db_node.find_node("Minuman")          
            if start_node:
                traverse_and_filter(start_node, [])

        unique_results = list(set(results)) 
        self.results_text.delete("1.0", "end")
        if unique_results:
            self.results_text.insert("end", "Makanan/Minuman yang ditemukan:\n")
            for item in unique_results:
                self.results_text.insert("end", f"🟠{item}\n")
        else:
            self.results_text.insert("end", "Tidak ada makanan/minuman yang cocok dengan kriteria Anda.")
        
        self.history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "query": search_query_str,
            "results": unique_results
        })
        self.save_data() 
         
    def setup_search_widgets(self):
        """Mengatur widget untuk frame pencarian."""
        ctk.CTkLabel(self.search_frame, text="Pencarian Makanan", font=("Arial", 24), text_color="#333333").pack(pady=20)
        self.results_text = ctk.CTkTextbox(self.search_frame, height=200, fg_color="#FFFFFF", text_color="#333333")
        info_label_search = ctk.CTkLabel(self.search_frame, text="Pencarian dilakukan pada Database Contoh (FNB_Database_Dummy).", text_color="#333333")
        info_label_search.pack(pady=5)
        
        search_criteria_frame = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        search_criteria_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(search_criteria_frame, text="Jenis Konsumsi:", text_color="#333333").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.search_consumption_type_var = ctk.StringVar(value="Makanan")
        for i, c_type in enumerate(["Makanan", "Minuman"]):
            ctk.CTkRadioButton(
                search_criteria_frame,
                text=c_type,
                variable=self.search_consumption_type_var,
                value=c_type,
                text_color="#333333",
                fg_color="#4CAF50"
            ).grid(row=0, column=i+1, padx=5, pady=5)
        self.search_consumption_type_var.trace_add("write", self.update_search_criteria_options) 

        self.food_criteria_frame = ctk.CTkFrame(search_criteria_frame, fg_color="transparent")
        self.food_criteria_frame.grid(row=1, column=0, columnspan=5, sticky="w", padx=0, pady=0)
        
        self.drink_criteria_frame = ctk.CTkFrame(search_criteria_frame, fg_color="transparent")
        self.drink_criteria_frame.grid(row=1, column=0, columnspan=5, sticky="w", padx=0, pady=0)

        self.setup_food_search_criteria_widgets(self.food_criteria_frame)
        self.setup_drink_search_criteria_widgets(self.drink_criteria_frame)

        self.update_search_criteria_options() 

        ctk.CTkLabel(search_criteria_frame, text="Alergi:", text_color="#333333").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.search_allergy_vars = {}
        for i, allergy in enumerate(self.ALLERGEN_OPTIONS):

            var = ctk.BooleanVar()
            col = i % 3 + 1 
            row = 4 + (i // 3)
            ctk.CTkCheckBox(
                search_criteria_frame,
                text=allergy,
                variable=var,
                text_color="#333333",
                fg_color="#4CAF50"
            ).grid(row=row, column=col, padx=5, pady=2, sticky="w")
            self.search_allergy_vars[allergy] = var
       
        # Frame untuk tombol berdampingan
        button_row = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        button_row.pack(pady=10)

        ctk.CTkButton(
            button_row, 
            text="Cari Makanan", 
            command=self.perform_search,
            fg_color="#007BFF",
            hover_color="#0056b3",
            width=150
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_row, 
            text="Kembali", 
            command=self.show_main_menu,
            fg_color="#dc3545",
            hover_color="#c82333",
            width=150
        ).pack(side="left", padx=10)

        self.results_text.pack(pady=10, padx=10, fill="both", expand=True)
        ctk.CTkButton(
            self.search_frame, 
            text="Visualisasi Pencarian DFS", 
            command=self.visualize_dfs_search, 
            fg_color="#6f42c1", 
            hover_color="#5a38a1"
        ).pack(pady=5)

    def setup_food_search_criteria_widgets(self, parent_frame):
        for widget in parent_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(parent_frame, text="Waktu Konsumsi:", text_color="#333333").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.search_jenis_makanan_var = ctk.StringVar(value="Makanan Berat")
        for i, jenis in enumerate(["Makanan Berat", "Makanan Ringan"]):
            ctk.CTkRadioButton(
                parent_frame,
                text=jenis,
                variable=self.search_jenis_makanan_var,
                value=jenis,
                text_color="#333333",
                fg_color="#4CAF50"
            ).grid(row=0, column=i+1, padx=5, pady=5)
        
        ctk.CTkLabel(parent_frame, text="Kategori:", text_color="#333333").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.search_category_var = ctk.StringVar(value="Bebas")
        for i, category in enumerate(["Bebas", "Tanpa Sayur", "Vegetarian", "Vegan"]):
            ctk.CTkRadioButton(
                parent_frame,
                text=category,
                variable=self.search_category_var,
                value=category,
                text_color="#333333",
                fg_color="#4CAF50"
            ).grid(row=1, column=i+1, padx=5, pady=5)
    
        ctk.CTkLabel(parent_frame, text="Tekstur:", text_color="#333333").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.search_texture_var = ctk.StringVar(value="Kering")
        for i, texture in enumerate(["Kering", "Berkuah"]):
            ctk.CTkRadioButton(
                parent_frame,
                text=texture,
                variable=self.search_texture_var,
                value=texture,
                text_color="#333333",
                fg_color="#4CAF50"
            ).grid(row=2, column=i+1, padx=5, pady=5)

        ctk.CTkLabel(parent_frame, text="Rasa:", text_color="#333333").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.search_taste_vars = {}
        tastes = ["Manis", "Asin/Gurih", "Asam", "Pahit", "Pedas"]
        for i, taste in enumerate(tastes):
            var = ctk.BooleanVar()
            col = i % 3 + 1
            row = 3 + (i // 3)
            ctk.CTkCheckBox(
                parent_frame,
                text=taste,
                variable=var,
                text_color="#333333",
                fg_color="#4CAF50"
            ).grid(row=row, column=col, padx=5, pady=2, sticky="w")
            self.search_taste_vars[taste] = var

    def setup_drink_search_criteria_widgets(self, parent_frame):
        for widget in parent_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(parent_frame, text="Suhu Minuman:", text_color="#333333").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.search_suhu_minuman_var = ctk.StringVar(value="Panas")
        for i, suhu in enumerate(["Panas", "Dingin"]):
            ctk.CTkRadioButton(
                parent_frame,
                text=suhu,
                variable=self.search_suhu_minuman_var,
                value=suhu,
                text_color="#333333",
                fg_color="#4CAF50"
            ).grid(row=0, column=i+1, padx=5, pady=5)

        ctk.CTkLabel(parent_frame, text="Rasa:", text_color="#333333").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.search_drink_taste_vars = {}
        tastes_minuman = ["Manis", "Asin", "Asam", "Pahit", "Pedas"] 
        for i, taste in enumerate(tastes_minuman):
            var = ctk.BooleanVar()
            col = i % 3 + 1
            row = 1 + (i // 3)
            ctk.CTkCheckBox(
                parent_frame,
                text=taste,
                variable=var,
                text_color="#333333",
                fg_color="#4CAF50"
            ).grid(row=row, column=col, padx=5, pady=2, sticky="w")
            self.search_drink_taste_vars[taste] = var
    
    def update_search_criteria_options(self, *args):
        selected_type = self.search_consumption_type_var.get()
        if selected_type == "Makanan":
            self.food_criteria_frame.tkraise()
            self.food_criteria_frame.grid(row=1, column=0, columnspan=5, sticky="w", padx=0, pady=0)
            self.drink_criteria_frame.grid_forget()
        elif selected_type == "Minuman":
            self.drink_criteria_frame.tkraise()
            self.drink_criteria_frame.grid(row=1, column=0, columnspan=5, sticky="w", padx=0, pady=0)
            self.food_criteria_frame.grid_forget()

    def setup_history_widgets(self):
        ctk.CTkLabel(self.history_frame, text="Riwayat Pencarian", font=("Arial", 24), text_color="#333333").pack(pady=20)
        
        self.history_text = ctk.CTkTextbox(self.history_frame, height=400, fg_color="#FFFFFF", text_color="#333333")
        self.history_text.pack(pady=10, padx=10, fill="both", expand=True)
        
        ctk.CTkButton(
            self.history_frame, 
            text="Kembali", 
            command=self.show_main_menu,
            fg_color="#dc3545",
            hover_color="#c82333"
        ).pack(pady=10)
        ctk.CTkButton(
            self.history_frame, 
            text="Hapus Riwayat", 
            command=self.clear_history,
            fg_color="#FFC107",
            hover_color="#E0A800"
        ).pack(pady=10)
        ctk.CTkButton(
            self.history_frame, 
            text="Ekspor Riwayat", 
            command=self.export_history,
            fg_color="#17A2B8",
            hover_color="#138496"
        ).pack(pady=10)
        ctk.CTkButton(
            self.history_frame, 
            text="Impor Riwayat", 
            command=self.import_history,
            fg_color="#28A745",
            hover_color="#218838"
        ).pack(pady=10)

    def setup_profile_widgets(self):
        ctk.CTkLabel(self.profile_frame, text="Profil Saya", font=("Arial", 24), text_color="#333333").pack(pady=20)
        
        self.profile_info_frame = ctk.CTkFrame(self.profile_frame, fg_color="transparent")
        self.profile_info_frame.pack(pady=10, padx=10, fill="x")
        
        self.username_label = ctk.CTkLabel(self.profile_info_frame, text="", font=("Arial", 14), text_color="#333333")
        self.username_label.pack(pady=5, anchor="w")
        
        self.preferences_label = ctk.CTkLabel(self.profile_info_frame, text="Preferensi Makanan:", font=("Arial", 14, "bold"), text_color="#333333")
        self.category_label = ctk.CTkLabel(self.profile_info_frame, text="", text_color="#333333")
        self.allergies_label = ctk.CTkLabel(self.profile_info_frame, text="", text_color="#333333")
        
        self.fill_button = ctk.CTkButton(
            self.profile_info_frame,
            text="Isi Preferensi Sekarang",
            command=lambda: [self.show_quiz(), self.profile_frame.pack_forget()],
            fg_color="#4CAF50",
            hover_color="#45a049"
        )     
        ctk.CTkButton(
            self.profile_frame, 
            text="Kembali", 
            command=self.show_main_menu,
            fg_color="#dc3545",
            hover_color="#c82333"
        ).pack(pady=10)
    
    def update_profile_info(self):
        user_data = self.users_data.get(self.current_user, {})
        quiz_answers = user_data.get("quiz_answers", {})
        
        self.username_label.configure(text=f"Username: {self.current_user}")
        
        if quiz_answers:
            self.preferences_label.pack(pady=5, anchor="w")
            self.category_label.configure(text=f"Kategori: {quiz_answers.get('category', 'Belum diisi')}")
            self.category_label.pack(pady=2, anchor="w")
            self.allergies_label.configure(text=f"Alergi: {', '.join(quiz_answers.get('allergies', ['Belum diisi']))}")
            self.allergies_label.pack(pady=2, anchor="w")
            self.fill_button.pack_forget()
        else:
            self.preferences_label.pack_forget()
            self.category_label.pack_forget()
            self.allergies_label.pack_forget()
            self.fill_button.pack(pady=10)
    
    def update_history_info(self):
        self.history_text.delete("1.0", "end") 
        if not self.history:
            self.history_text.insert("end", "Belum ada riwayat pencarian.")
        else:
            for i, search in enumerate(reversed(self.history), 1):
                self.history_text.insert("end", f"{i}. {search['query']} - {search['time']}")
                self.history_text.insert("end", f"Hasil: {len(search['results'])} makanan ditemukan:n")
    
    def show_login(self):
        self.hide_all_frames()
        self.login_frame.pack(fill="both", expand=True)
        self.username_entry.focus()
    
    def show_register(self):
        self.hide_all_frames()
        self.register_frame.pack(fill="both", expand=True)
        self.new_username_entry.focus()
    
    def show_quiz(self):
        self.hide_all_frames()
        self.quiz_frame.pack(fill="both", expand=True)
    
    def show_main_menu(self):
        self.hide_all_frames()
        self.main_menu_label.configure(text=f"Selamat datang, {self.current_user}!")
        self.main_menu_frame.pack(fill="both", expand=True)
    
    def show_database(self):
        self.hide_all_frames()
        self.database_frame.pack(fill="both", expand=True)
        self.refresh_tree()
    
    def show_search(self):
        self.hide_all_frames()
        self.search_frame.pack(fill="both", expand=True)
        
        user_data = self.users_data.get(self.current_user, {})
        quiz_answers = user_data.get("quiz_answers", {})
        
        if quiz_answers:
            user_allergies = quiz_answers.get("allergies", [])
            for allergy, var in self.search_allergy_vars.items():
                var.set(allergy in user_allergies)
    
    def show_history(self):
        self.hide_all_frames()
        self.history_frame.pack(fill="both", expand=True)
        self.update_history_info()
    
    def show_profile(self):
        self.hide_all_frames()
        self.profile_frame.pack(fill="both", expand=True)
        self.update_profile_info()
    
    def hide_all_frames(self):
        for frame in [
            self.login_frame, 
            self.register_frame, 
            self.quiz_frame,
            self.main_menu_frame,
            self.database_frame,
            self.search_frame,
            self.history_frame,
            self.profile_frame
        ]:
            frame.pack_forget()
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Username dan password harus diisi")
            return
        if username not in self.users_data:
            messagebox.showerror("Error", "Username tidak ditemukan")
            return
        if self.users_data[username]["password"] != password:
            messagebox.showerror("Error", "Password salah")
            return
        
        self.current_user = username
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        
        if "quiz_answers" not in self.users_data[username] or self.users_data[username]["quiz_answers"] is None:
            self.show_quiz()
        else:
            self.show_main_menu()
    
    def register(self):
        username = self.new_username_entry.get().strip()
        password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        
        if not username or not password or not confirm_password:
            messagebox.showerror("Error", "Semua field harus diisi")
            return 
        if len(username) < 4:
            messagebox.showerror("Error", "Username minimal 4 karakter") 
            return 
        if len(password) < 6:
            messagebox.showerror("Error", "Password minimal 6 karakter")
            return
        if password != confirm_password:
            messagebox.showerror("Error", "Password tidak cocok")
            return
        if username in self.users_data:
            messagebox.showerror("Error", "Username sudah digunakan")
            return
 
        self.users_data[username] = {
            "password": password,
            "quiz_answers": None  
        } 
        self.save_data()
        
        messagebox.showinfo("Sukses", "Registrasi berhasil! Silakan login")
        self.show_login()
        self.new_username_entry.delete(0, "end")
        self.new_password_entry.delete(0, "end")
        self.confirm_password_entry.delete(0, "end")
    
    def submit_quiz(self):
        category = self.category_var.get()
        allergies = [allergy for allergy, var in self.allergy_vars.items() if var.get()] 
        if not allergies:
            if not messagebox.askyesno("Konfirmasi", "Anda tidak memilih alergi apapun. Lanjutkan?"):
                return 
        self.users_data[self.current_user]["quiz_answers"] = {
            "category": category,
            "allergies": allergies
        } 
        self.save_data()
        messagebox.showinfo("Sukses", "Preferensi makanan telah disimpan!")
        self.show_main_menu()
    
    def logout(self):
        self.current_user = None
        self.show_login()
    
    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        if self.food_db: 
            main_node_id = self.tree.insert("", "end", text=self.food_db.name, open=True) 
            for child_node in self.food_db.children:
                self._insert_nodes_to_treeview(main_node_id, child_node)
        else:
            self.tree.insert("", "end", text="Database makanan tidak dimuat atau kosong.")
     
    def _insert_nodes_to_treeview(self, parent_id, node):
        should_open_node = node.name in [self.DB_STRUCTURE_NAME, self.DB_DUMMY_NAME]

        new_id = self.tree.insert(parent_id, "end", text=node.name, open=should_open_node)
        for child in node.children:
            self._insert_nodes_to_treeview(new_id, child)
 
    def add_node(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih parent node terlebih dahulu.")
            return
        parent_name_in_tree = self.tree.item(selected_item, "text")
        
        dialog = ctk.CTkInputDialog(text=f"Nama node baru untuk '{parent_name_in_tree}':", title="Tambah Node")
        new_node_name = dialog.get_input()

        if new_node_name and new_node_name.strip() != "":
            parent_node_in_db = self._find_treenode_from_treeview_id(selected_item)

            if parent_node_in_db:
                if any(child.name == new_node_name.strip() for child in parent_node_in_db.children):
                    messagebox.showwarning("Peringatan", f"Node dengan nama '{new_node_name}' sudah ada di bawah parent ini.")
                    return   
                TreeNode(new_node_name.strip(), parent_node_in_db)
                self.save_data()
                self.refresh_tree()
                messagebox.showinfo("Sukses", f"Node '{new_node_name}' berhasil ditambahkan.")
            else:
                messagebox.showerror("Error", "Parent node tidak ditemukan di struktur data.")
        elif new_node_name and new_node_name.strip() == "":
            messagebox.showwarning("Peringatan", "Nama node tidak boleh kosong.")

    def edit_node(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih node yang ingin diedit.")
            return

        old_name = self.tree.item(selected_item, "text")

        dialog = ctk.CTkInputDialog(text=f"Edit nama node '{old_name}':", title="Edit Node", initial_text=old_name)
        new_name = dialog.get_input()

        if new_name and new_name.strip() != "" and new_name != old_name:
            node_to_edit = self._find_treenode_from_treeview_id(selected_item)
    
            if node_to_edit:
                if node_to_edit == self.food_db: 
                    messagebox.showwarning("Peringatan", "Tidak bisa mengedit root node 'Main'.")
                    return
                if node_to_edit.name in [self.DB_STRUCTURE_NAME, self.DB_DUMMY_NAME] and node_to_edit.parent == self.food_db:
                    messagebox.showwarning("Peringatan", f"Tidak bisa mengedit node utama '{node_to_edit.name}'.")
                    return
                if node_to_edit.parent:
                    if any(sibling.name == new_name.strip() for sibling in node_to_edit.parent.children if sibling != node_to_edit):
                        messagebox.showwarning("Peringatan", f"Nama '{new_name.strip()}' sudah ada di level ini.")
                        return
                    
                node_to_edit.name = new_name.strip()
                self.save_data()
                self.refresh_tree()
                messagebox.showinfo("Sukses", f"Node '{old_name}' berhasil diubah menjadi '{new_name}'.")
            else:
                messagebox.showerror("Error", "Gagal menemukan node di struktur data.")
        elif new_name and new_name.strip() == "":
            messagebox.showwarning("Peringatan", "Nama node tidak boleh kosong.")
        elif new_name == old_name:
            messagebox.showinfo("Info", "Nama node tidak berubah.")
    
    def add_parent(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih node yang ingin dijadikan anak dari parent baru.")
            return
    
        child_node_name = self.tree.item(selected_item, "text")
        parent_iid_old_tree = self.tree.parent(selected_item)
    
        if not parent_iid_old_tree: 
            messagebox.showwarning("Peringatan", "Tidak bisa menambahkan parent di atas root node 'Main'.")
            return
        
        dialog = ctk.CTkInputDialog(text=f"Nama parent node baru untuk '{child_node_name}':", title="Tambah Parent")
        new_parent_name = dialog.get_input()
    
        if new_parent_name and new_parent_name.strip() != "":
            child_node_obj = self._find_treenode_from_treeview_id(selected_item)
    
            if child_node_obj and child_node_obj.parent:
                old_parent_node_in_db = child_node_obj.parent
            
                if child_node_obj.name in [self.DB_STRUCTURE_NAME, self.DB_DUMMY_NAME] and old_parent_node_in_db == self.food_db:
                    messagebox.showwarning("Peringatan", f"Tidak bisa menambahkan parent untuk node utama '{child_node_obj.name}'.")
                    return
                if any(sibling.name == new_parent_name.strip() for sibling in old_parent_node_in_db.children):
                    messagebox.showwarning("Peringatan", f"Node dengan nama '{new_parent_name.strip()}' sudah ada di bawah parent ini.")
                    return
    
                new_parent_obj = TreeNode(new_parent_name.strip(), old_parent_node_in_db)
                old_parent_node_in_db.remove_child(child_node_obj)
                child_node_obj.parent = new_parent_obj 
                new_parent_obj.add_child(child_node_obj)
    
                self.save_data()
                self.refresh_tree()
                messagebox.showinfo("Sukses", f"Node '{new_parent_name}' berhasil ditambahkan sebagai parent dari '{child_node_name}'.")
            else:
                messagebox.showerror("Error", "Gagal menemukan parent atau child node di struktur data.")
        elif new_parent_name and new_parent_name.strip() == "":
            messagebox.showwarning("Peringatan", "Nama parent node tidak boleh kosong.")
    
    def delete_node(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih node yang ingin dihapus.")
            return
        
        node_name_to_delete = self.tree.item(selected_item, "text")
        parent_iid_tree = self.tree.parent(selected_item)
    
        if not parent_iid_tree: 
            messagebox.showwarning("Peringatan", "Anda tidak bisa menghapus root node 'Main'.")
            return
    
        if messagebox.askyesno("Konfirmasi Hapus", f"Apakah Anda yakin ingin menghapus node '{node_name_to_delete}' dan semua child-nya?"):
            node_to_delete_obj = self._find_treenode_from_treeview_id(selected_item)
    
            if node_to_delete_obj and node_to_delete_obj.parent:
                if node_to_delete_obj.name in [self.DB_STRUCTURE_NAME, self.DB_DUMMY_NAME] and node_to_delete_obj.parent == self.food_db:
                    messagebox.showwarning("Peringatan", f"Tidak bisa menghapus node utama '{node_to_delete_obj.name}'. Hapus isinya jika perlu.")
                    return
                
                parent_of_deleted_node = node_to_delete_obj.parent
                if parent_of_deleted_node.remove_child(node_to_delete_obj):
                    self.save_data()
                    self.refresh_tree() 
                    messagebox.showinfo("Sukses", f"Node '{node_name_to_delete}' berhasil dihapus.")
                else:
                    messagebox.showerror("Error", "Gagal menghapus node dari struktur data internal.")
            elif node_to_delete_obj == self.food_db: 
                messagebox.showwarning("Peringatan", "Tidak bisa menghapus root node 'Main' lewat sini.")
            else:
                messagebox.showerror("Error", "Node tidak ditemukan atau tidak memiliki parent di struktur data.")
    
    def _get_path_names_from_treeview_id(self, iid):
        path_names = []
        current_iid = "iid"
        
        current_iid = iid
        while current_iid: 
            path_names.insert(0, self.tree.item(current_iid, "text"))
            current_iid = self.tree.parent(current_iid)
        return path_names 
    
    def _find_treenode_from_treeview_id(self, iid_to_find):
        """Mencari objek TreeNode berdasarkan ID item Treeview."""
        path_names = self._get_path_names_from_treeview_id(iid_to_find)
        if not path_names or not self.food_db:
            return None
        if path_names[0] != self.food_db.name:
            return None 
            current_treenode = self.food_db
        if len(path_names) == 1 and path_names[0] == self.food_db.name:
            return self.food_db 
        for name_segment in path_names[1:]:
            found_child = None
            for child in current_treenode.children:
                if child.name == name_segment:
                    found_child = child
                    break
            if not found_child:
                return None 
            current_treenode = found_child
        
        return current_treenode 
    
    def get_node_path(self, item):
        path = []
        while item:
            path.append(self.tree.item(item, "text"))
            item = self.tree.parent(item)
        return path[::-1]  
    
    def find_node_by_path_names(self, iid, current_root_node):
        path = []
        current_iid = iid
        while current_iid:
            path.insert(0, self.tree.item(current_iid, "text"))
            current_iid = self.tree.parent(current_iid)
        
        if path and path[0] == self.food_db.name:
            path.pop(0)
        node = current_root_node
        for name in path:
            found_child = None
            for child in node.children:
                if child.name == name:
                    found_child = child
                    break
            if not found_child:
                return None 
            node = found_child
        return node
    
    def visualize_tree(self):
        if not self.food_db:
            messagebox.showinfo("Info", "Database makanan kosong.")
            return
        dialog = ctk.CTkInputDialog(text="Pilih bagian database untuk divisualisasikan:n1. Struktur Databasen2. Contoh Database (Dummy)n3. Keseluruhan (Main)", title="Pilih Visualisasi")
        choice_str = dialog.get_input()
    
        root_to_visualize = None
        title_for_viz = ""
        if choice_str == "1":
            root_to_visualize = self.food_db.find_node(self.DB_STRUCTURE_NAME)
            title_for_viz = self.DB_STRUCTURE_NAME
        elif choice_str == "2":
            root_to_visualize = self.food_db.find_node(self.DB_DUMMY_NAME)
            title_for_viz = self.DB_DUMMY_NAME
        elif choice_str == "3":
            root_to_visualize = self.food_db 
            title_for_viz = self.food_db.name
        else:
            if choice_str is not None: 
                messagebox.showinfo("Info", "Pilihan tidak valid.")
            return
        if not root_to_visualize:
            messagebox.showinfo("Info", f"Bagian database '{title_for_viz}' tidak ditemukan atau kosong.")
            return
        VisualizationWindow(self.root, root_to_visualize)
    
    def _build_balanced_bst(self, sorted_list):
        if not sorted_list:
            return None
        
        mid = len(sorted_list) // 2
        root_val = sorted_list[mid]
        root = TreeNode(root_val) 
        left_child = self._build_balanced_bst(sorted_list[:mid])
        if left_child:
            root.children.append(left_child)
        else: 
            root.children.append(None) 
            
        right_child = self._build_balanced_bst(sorted_list[mid+1:])
        if right_child:
            root.children.append(right_child)
        else:
            root.children.append(None)   
        return root

    def _search_bst(self, node, target):
        if node is None:
            return None
        
        if target == node.name:
            return node
        elif target < node.name and len(node.children) > 0 and node.children[0]:
            return self._search_bst(node.children[0], target)
        elif target > node.name and len(node.children) > 1 and node.children[1]:
            return self._search_bst(node.children[1], target)
        return None

    def _get_all_leaf_names(self, node, leaf_names_list):
        if not node.children:
            leaf_names_list.append(node.name)
        else:
            for child in node.children:
                self._get_all_leaf_names(child, leaf_names_list)

    def get_search_criteria(self):
        criteria = {}
        search_type = self.search_consumption_type_var.get()
        criteria["Jenis Konsumsi"] = search_type

        if search_type == "Makanan":
            criteria["Waktu Konsumsi"] = self.search_jenis_makanan_var.get()
            criteria["Kategori"] = self.search_category_var.get()
            criteria["Tekstur"] = self.search_texture_var.get()
            
            selected_tastes = [taste for taste, var in self.search_taste_vars.items() if var.get()]
            if not selected_tastes: selected_tastes = ["Manis", "Asin/Gurih", "Asam", "Pahit", "Pedas"] 
            criteria["Rasa"] = selected_tastes
        elif search_type == "Minuman":
            criteria["Suhu"] = self.search_suhu_minuman_var.get()
            
            selected_tastes = [taste for taste, var in self.search_drink_taste_vars.items() if var.get()]
            if not selected_tastes: selected_tastes = ["Manis", "Asin", "Asam", "Pahit", "Pedas"] 
            criteria["Rasa"] = selected_tastes

        selected_allergens = [allergy for allergy, var in self.search_allergy_vars.items() if var.get()]
        if not selected_allergens: selected_allergens = ["Tanpa Alergen"]
        criteria["Alergen"] = selected_allergens   
        return criteria

    def format_search_query(self, criteria):
        parts = []
        parts.append(f"Jenis Konsumsi: {criteria.get('Jenis Konsumsi')}")
        if criteria.get("Jenis Konsumsi") == "Makanan":
            parts.append(f"Waktu Konsumsi: {criteria.get('Waktu Konsumsi')}")
            parts.append(f"Kategori: {criteria.get('Kategori')}")
            parts.append(f"Tekstur: {criteria.get('Tekstur')}")
        elif criteria.get("Jenis Konsumsi") == "Minuman":
            parts.append(f"Suhu: {criteria.get('Suhu')}")

        parts.append(f"Rasa: {', '.join(criteria.get('Rasa', []))}")
        parts.append(f"Alergen: {', '.join(criteria.get('Alergen', []))}")
        return "; ".join(parts)
    
    def clear_history(self):
        if  messagebox.askyesno("Konfirmasi", "Hapus semua riwayat pencarian?"):
                self.history.clear()
                self.update_history_info()
                messagebox.showinfo("Sukses", "Riwayat pencarian telah dihapus.")
                self.history_text.delete("1.0", "end")
    
    def export_history(self):
        if self.history:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
            if file_path:
                with open(file_path, "w", newline="", encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Waktu", "Query", "Hasil"])
                    for entry in self.history:
                        writer.writerow([entry["time"], entry["query"], "n".join(entry["results"])])
                messagebox.showinfo("Sukses", "Riwayat pencarian berhasil diekspor.")
            else:
                messagebox.showinfo("Info", "Ekspor dibatalkan.")

    def import_history(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                with open(file_path, "r", newline="", encoding='utf-8') as file:
                    reader = csv.reader(file)
                    header = next(reader)  # Skip header
                    if header != ["Waktu", "Query", "Hasil"]:
                        raise ValueError("Format file CSV tidak valid.")
                    
                    for row in reader:
                        if len(row) == 3:
                            time, query, results = row
                            results_list = results.split("n") if results else []
                            self.history.append({
                                "time": time,
                                "query": query,
                                "results": results_list
                            })
                self.update_history_info()
                messagebox.showinfo("Sukses", "Riwayat pencarian berhasil diimpor.")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal mengimpor riwayat: {e}")

    def run(self):
        self.root.mainloop()

class VisualizationWindow(ctk.CTkToplevel):
    def __init__(self, master, tree_root_node):
        super().__init__(master)
        self.title(f"Visualisasi Tree: {tree_root_node.name}")
        self.geometry("1200x700")
        self.configure(fg_color="#FFFDD0") 
        self.tree_root_node = tree_root_node 
        self.canvas = tk.Canvas(self, bg="#FFFDD0", highlightbackground="#FFFDD0") 
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar_x = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview)
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.configure(xscrollcommand=self.scrollbar_x.set)
        self.scrollbar_y = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        self.scrollbar_y.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set)
        self.canvas.bind("<ButtonPress-1>", self.scroll_start)
        self.canvas.bind("<B1-Motion>", self.scroll_move)
        self.canvas.bind("<MouseWheel>", self.zoom_mousewheel) 
        self.canvas.bind("<Button-4>", self.zoom_mousewheel) 
        self.canvas.bind("<Button-5>", self.zoom_mousewheel) 
        self.scale_factor = 1.0
        self.node_positions = {} 
        self.draw_tree()

    def scroll_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, checkdrag=1)

    def zoom_mousewheel(self, event):
        if event.delta > 0 or event.num == 4:  
            self.scale_factor *= 1.1
        elif event.delta < 0 or event.num == 5:  
            self.scale_factor /= 1.1
        self.draw_tree()

    def draw_tree(self):
        self.canvas.delete("all")
        if not self.tree_root_node:
            return

        node_width = 120 
        node_height = 40
        x_spacing_min = 30 
        y_spacing = 80  

        self.node_positions.clear() 
        leaf_x_counter = [50] 

        def calculate_subtree_layout(node, level):
            if not node:
                return {'min_x': float('inf'), 'max_x': float('-inf')}

            if not node.children: 
                x = leaf_x_counter[0]
                self.node_positions[node] = (x, level * y_spacing + 50)
                leaf_x_counter[0] += (node_width + x_spacing_min)
                return {'min_x': x, 'max_x': x}
            
            min_child_x = float('inf')
            max_child_x = float('-inf')
            
            for child in node.children:
                child_layout = calculate_subtree_layout(child, level + 1)
                min_child_x = min(min_child_x, child_layout['min_x'])
                max_child_x = max(max_child_x, child_layout['max_x'])
            
            node_x = (min_child_x + max_child_x) / 2
            self.node_positions[node] = (node_x, level * y_spacing + 50)
            
            return {'min_x': min_child_x, 'max_x': max_child_x}

        calculate_subtree_layout(self.tree_root_node, 0)
        max_canvas_x = 0
        max_canvas_y = 0

        for node, (x, y) in self.node_positions.items():
            for child in node.children:
                if child in self.node_positions:
                    x1, y1 = self.node_positions[node]
                    x2, y2 = self.node_positions[child]
                    self.canvas.create_line(x1 * self.scale_factor, (y1 + node_height/2) * self.scale_factor,
                                            x2 * self.scale_factor, (y2 - node_height/2) * self.scale_factor,
                                            fill="#666666", width=1.5)
            
            x_scaled, y_scaled = x * self.scale_factor, y * self.scale_factor
            current_node_actual_width = max(node_width, len(node.name) * 8) 
            width_scaled, height_scaled = current_node_actual_width * self.scale_factor, node_height * self.scale_factor

            self.canvas.create_rectangle(
                x_scaled - width_scaled / 2, y_scaled - height_scaled / 2,
                x_scaled + width_scaled / 2, y_scaled + height_scaled / 2,
                fill="#87CEEB", outline="#0056b3", width=2, tags="node"
            )
            self.canvas.create_text(
                x_scaled, y_scaled,
                text=node.name, font=("Arial", int(10 * self.scale_factor)), fill="#333333", tags="node_text"
            ) 
            max_canvas_x = max(max_canvas_x, x_scaled + width_scaled / 2)
            max_canvas_y = max(max_canvas_y, y_scaled + height_scaled / 2)
        self.canvas.config(scrollregion=(0, 0, max_canvas_x + 100, max_canvas_y + 100)) 
        
class DFSSearchVisualizationWindow(ctk.CTkToplevel):
    def __init__(self, master, tree_root_node, visited_steps, matched_nodes, title_text):
        super().__init__(master)
        self.title(title_text)
        self.geometry("1200x700")
        self.configure(fg_color="#FFFDD0")

        self.tree_root_node = tree_root_node 
        self.all_nodes = {} 
        self._collect_all_nodes(self.tree_root_node) 

        self.visited_steps_names = visited_steps 
        self.matched_nodes_names = set(matched_nodes) 
        self.current_step_index = 0

        self.canvas = tk.Canvas(self, bg="#FFFDD0", highlightbackground="#FFFDD0")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.is_playing = False
        self.animation_delay_ms = 1000 
        self.animation_job = None
        
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar_x = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview)
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.configure(xscrollcommand=self.scrollbar_x.set)

        self.scrollbar_y = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        self.scrollbar_y.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set)

        self.canvas.bind("<ButtonPress-1>", self.scroll_start)
        self.canvas.bind("<B1-Motion>", self.scroll_move)
        self.canvas.bind("<MouseWheel>", self.zoom_mousewheel)
        self.canvas.bind("<Button-4>", self.zoom_mousewheel)
        self.canvas.bind("<Button-5>", self.zoom_mousewheel)

        self.scale_factor = 1.0
        self.node_positions = {} 
        self.node_canvas_ids = {} 
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.pack(side="right", fill="y", padx=10)

        ctk.CTkLabel(controls_frame, text="Kontrol Visualisasi", font=("Arial", 14, "bold")).pack(pady=10)

        self.step_label = ctk.CTkLabel(controls_frame, text="Langkah: 0 / 0")
        self.step_label.pack(pady=5)
        self.play_pause_button = ctk.CTkButton(controls_frame, text="Play", command=self.toggle_play_pause)
        self.play_pause_button.pack(pady=5)
        ctk.CTkButton(controls_frame, text="Langkah Berikutnya", command=lambda: self.next_step(automated=False)).pack(pady=5)
        ctk.CTkButton(controls_frame, text="Mulai Ulang", command=self.reset_visualization).pack(pady=5) 
        ctk.CTkLabel(controls_frame, text="Kecepatan Animasi (detik):").pack(pady=(10,0))
        self.speed_slider = ctk.CTkSlider(controls_frame, from_=0.1, to=4.0, command=self.update_animation_speed)
        self.speed_slider.set(self.animation_delay_ms / 1000) # Set initial slider value
        self.speed_slider.pack(pady=5)
        self.speed_label = ctk.CTkLabel(controls_frame, text=f"{self.animation_delay_ms/1000:.1f} s")
        self.speed_label.pack(pady=(0,10))
        ctk.CTkButton(controls_frame, text="Mulai Ulang", command=self.reset_visualization).pack(pady=5)
        ctk.CTkButton(controls_frame, text="Selesai", command=self.destroy).pack(pady=20)
        self.calculate_node_positions() 
        self.draw_tree_structure() 
        self.update_visualization() 

    def destroy(self):
        if self.animation_job:
            self.after_cancel(self.animation_job)
            self.animation_job = None
        super().destroy()

    def update_animation_speed(self, value):
        self.animation_delay_ms = int(float(value) * 1000)
        self.speed_label.configure(text=f"{float(value):.1f} s")

    def toggle_play_pause(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_pause_button.configure(text="Pause")
            self._animate_step()
        else:
            self.play_pause_button.configure(text="Play")
            if self.animation_job:
                self.after_cancel(self.animation_job)
                self.animation_job = None

    def _collect_all_nodes(self, node):
        if not node:
            return
        self.all_nodes[node.name] = node
        for child in node.children:
            self._collect_all_nodes(child)
        print("selesai collect_all_nodes")

    def scroll_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, checkdrag=1)

    def zoom_mousewheel(self, event):
        if event.delta > 0 or event.num == 4:
            self.scale_factor *= 1.1
        elif event.delta < 0 or event.num == 5:
            self.scale_factor /= 1.1
        self.draw_tree_structure() 
        self.update_visualization() 

    def calculate_node_positions(self):
        print ("Memulai calculate_node_positions")
        node_width = 120
        node_height = 40
        x_spacing_min = 30
        y_spacing = 80

        self.node_positions.clear()
        subtree_widths = {}

        def get_subtree_width(node):
            if not node:
                return 0
            if node in subtree_widths:
                return subtree_widths[node]

            if not node.children:
                width = node_width + x_spacing_min
            else:
                width = sum(get_subtree_width(child) for child in node.children)

            subtree_widths[node] = width
            return width
        get_subtree_width(self.tree_root_node)
        print("selesai calculate_node_positions")
        
        def calculate_positions_recursive(node, x_offset, y_level):
            if not node:
                return
            node_x = x_offset + get_subtree_width(node) / 2
            node_y = y_level * y_spacing + 50
            self.node_positions[node.name] = (node_x, node_y)

            current_child_x_offset = x_offset
            for child in node.children:
                if child:
                    calculate_positions_recursive(child, current_child_x_offset, y_level + 1)
                    current_child_x_offset += get_subtree_width(child)
        calculate_positions_recursive(self.tree_root_node, 50, 0)

    def draw_tree_structure(self):
        print("Memulai draw_tree_structure")
        self.canvas.delete("all")
        self.node_canvas_ids.clear()

        if not self.tree_root_node or not self.node_positions:
            return

        node_width = 120
        node_height = 40

        max_canvas_x = 0
        max_canvas_y = 0
        
        def draw_lines_recursive(node):
            if not node or not node.children:
                return

            x1, y1 = self.node_positions[node.name]
            for child in node.children:
                if child and child.name in self.node_positions:
                    x2, y2 = self.node_positions[child.name]
                    self.canvas.create_line(x1 * self.scale_factor, (y1 + node_height/2) * self.scale_factor,
                                            x2 * self.scale_factor, (y2 - node_height/2) * self.scale_factor,
                                            fill="#666666", width=1.5, tags="tree_line")
                    draw_lines_recursive(child)

        draw_lines_recursive(self.tree_root_node)
        
        for node_name, (x, y) in self.node_positions.items():
            x_scaled, y_scaled = x * self.scale_factor, y * self.scale_factor
            current_node_actual_width = max(node_width, len(node_name) * 8)
            width_scaled, height_scaled = current_node_actual_width * self.scale_factor, node_height * self.scale_factor

            rect_id = self.canvas.create_rectangle(
                x_scaled - width_scaled / 2, y_scaled - height_scaled / 2,
                x_scaled + width_scaled / 2, y_scaled + height_scaled / 2,
                fill="#87CEEB", outline="#0056b3", width=2, tags="node_shape"
            )
            text_id = self.canvas.create_text(
                x_scaled, y_scaled,
                text=node_name, font=("Arial", int(10 * self.scale_factor)), fill="#333333", tags="node_text"
            )
            self.node_canvas_ids[node_name] = (rect_id, text_id) 

            max_canvas_x = max(max_canvas_x, x_scaled + width_scaled / 2)
            max_canvas_y = max(max_canvas_y, y_scaled + height_scaled / 2)

        self.canvas.config(scrollregion=(0, 0, max_canvas_x + 100, max_canvas_y + 100))

        print("Selesai draw_tree_structure")

    def update_visualization(self):
        """Updates node highlighting based on the current step."""
        # Reset all node colors
        for rect_id, text_id in self.node_canvas_ids.values():
            self.canvas.itemconfig(rect_id, fill="#87CEEB", outline="#0056b3") 
            self.canvas.itemconfig(text_id, fill="#333333") 

        for i in range(self.current_step_index + 1):
            if i < len(self.visited_steps_names):
                node_name = self.visited_steps_names[i]
                if node_name in self.node_canvas_ids:
                    rect_id, text_id = self.node_canvas_ids[node_name]
                    # Highlight visited nodes
                    self.canvas.itemconfig(rect_id, fill="#FFFF99", outline="#FFA500") 
                    self.canvas.itemconfig(text_id, fill="#000000") 

        if self.current_step_index < len(self.visited_steps_names):
            current_node_name = self.visited_steps_names[self.current_step_index]
            if current_node_name in self.node_canvas_ids:
                rect_id, text_id = self.node_canvas_ids[current_node_name]
                # Highlight current node
                self.canvas.itemconfig(rect_id, fill="#FF6347", outline="#DC143C") 
                self.canvas.itemconfig(text_id, fill="#FFFFFF") 
                if current_node_name in self.matched_nodes_names:
                    self.canvas.itemconfig(rect_id, fill="#4CAF50", outline="#218838") 
                    self.canvas.itemconfig(text_id, fill="#FFFFFF") 
        self.update_step_label()

    def _animate_step(self):
        if not self.is_playing:
            return 
        if self.current_step_index < len(self.visited_steps_names) -1:
            self.next_step(automated=True)
            self.animation_job = self.after(self.animation_delay_ms, self._animate_step)
        elif self.current_step_index == len(self.visited_steps_names) -1: 
            self.next_step(automated=True) 
            self.is_playing = False
            self.play_pause_button.configure(text="Play")
            messagebox.showinfo("Info", "Visualisasi selesai.", parent=self)
        else: 
            self.is_playing = False
            self.play_pause_button.configure(text="Play")
    
    def next_step(self, automated=False):
        """Moves to the next step in the visualization."""
        if self.current_step_index < len(self.visited_steps_names) - 1:
            self.current_step_index += 1
            self.update_visualization()
        elif self.current_step_index == len(self.visited_steps_names) - 1:
            self.current_step_index += 1 
            self.update_visualization() 
            if not automated:
                messagebox.showinfo("Info", "Visualisasi selesai.", parent=self)
        elif not automated: # Already past the end, manual click
            messagebox.showinfo("Info", "Visualisasi sudah selesai.", parent=self)

    def reset_visualization(self):
        if self.animation_job:
            self.after_cancel(self.animation_job)
            self.animation_job = None
        self.is_playing = False
        self.play_pause_button.configure(text="Play")

        self.current_step_index = 0
        self.update_visualization()
    
    def update_step_label(self):
        total_steps = len(self.visited_steps_names)
        display_step = min(self.current_step_index + 1, total_steps) 
        if self.current_step_index >= total_steps:
            self.step_label.configure(text=f"Selesai ({total_steps} langkah)")
        else:
            self.step_label.configure(text=f"Langkah: {display_step} / {total_steps}")

if __name__ == "__main__":
    app = App()
    app.run()