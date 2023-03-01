import os
import random
import shutil
from subprocess import call

import matplotlib.pyplot as plt
from PIL import Image

from get_user_input import user_select_folder, user_do_pair, finish_windows

import pandas as pd


class PairsPhoto:
    photos_folder = None
    all_sub_folder = None
    train_a_path = None
    train_b_path = None
    train_a_start_index = 0
    train_b_start_index = 0
    
    skip_folder = None
    skip_folder_log = None
    
    def __init__(self):
        # get the root folder
        self.photos_folder = user_select_folder()
        
        self.train_a_path = os.path.join(os.getcwd(), 'datasets', 'trainA')
        if not os.path.exists(self.train_a_path):
            os.makedirs(self.train_a_path)
        self.train_b_path = os.path.join(os.getcwd(), 'datasets', 'trainB')
        if not os.path.exists(self.train_b_path):
            os.makedirs(self.train_b_path)
            
        self.train_a_start_index = len(
            [f for f in os.listdir(self.train_a_path) if f.lower().endswith(
                ('.png', '.jpg', '.jpeg', '.gif'))])
        self.train_b_start_index = len(
            [f for f in os.listdir(self.train_b_path) if f.lower().endswith(
                ('.png', '.jpg', '.jpeg', '.gif'))])
        
        assert self.train_a_start_index == self.train_b_start_index
        # Get a list of all the photo file names in the folder
        photo_files = [f for f in os.listdir(self.photos_folder) if
                       os.path.isfile(
                           os.path.join(self.photos_folder, f)) and f.endswith(
                           '.jpg')]
        
        for f in photo_files:
            time_folder = os.path.join(self.photos_folder, f.split('_UTC_')[0])
            if not os.path.exists(time_folder):
                os.makedirs(time_folder)
            shutil.move(os.path.join(self.photos_folder, f), time_folder)
        
        # find all JPG files under the photos_folder and its time subfolders
        self.all_sub_folder = [f.path for f in os.scandir(self.photos_folder)
                               if
                               f.is_dir() and f.name[:5] != 'train']
                
        # for the paired photo log
        csv_log = os.path.join(self.photos_folder, "paired_folder.csv")
        if os.path.exists(csv_log):
            print("loading the paired folder log...")
            self.skip_folder_log = pd.read_csv(csv_log)
            self.skip_folder = self.skip_folder_log[
                'skip_folder'].values.tolist()
        else:
            print("making the paired folder log...")
            self.skip_folder = []
            self.skip_folder_log = pd.DataFrame(
                {"skip_folder": self.skip_folder})
            self.skip_folder_log.to_csv(csv_log, index=False)
    
    def update_skip_folder_log(self):
        csv_log = os.path.join(self.photos_folder, "paired_folder.csv")
        self.skip_folder_log = pd.DataFrame({"skip_folder": self.skip_folder})
        self.skip_folder_log.to_csv(csv_log, index=False)
    
    def pick_one_folder(self):
        photo_list, photo_p = None, None
        for photo_p in self.all_sub_folder:
            if photo_p in self.skip_folder:
                continue
            
            photo_list = [os.path.join(photo_p, f) for f in
                          os.listdir(photo_p) if
                          os.path.isfile(os.path.join(photo_p, f))]
            photo_list = [f for f in photo_list if f.lower().endswith(
                ('.png', '.jpg', '.jpeg', '.gif'))]
            if len(photo_list) <= 1:
                photo_list = None
                self.skip_folder.append(photo_p)
                continue
            else:
                break
        
        self.update_skip_folder_log()
        return photo_p, photo_list
    
    def generate_bg_png(self, photo_list, first_photo_as=None):
        # Load and display the first photo
        if first_photo_as:
            first_photo_path = first_photo_as
        else:
            first_photo_path = random.choice(photo_list)
        first_photo_image = Image.open(first_photo_path)
        # select pair candidate for the first img
        candidates = [f for f in photo_list if f != first_photo_path]
        # Create the figure and gridspec
        fig = plt.figure(constrained_layout=True, figsize=(14, 7))
        gs = fig.add_gridspec(5, 5,
                              wspace=0.01, hspace=0.01,
                              # width_ratios=[1, 1, 1, 50, 50],
                              # height_ratios=[50,50,50, 150, 150],
                              )
        # Add the large photo on the left
        ax1 = fig.add_subplot(gs[:3, :3])
        ax1.imshow(first_photo_image)
        ax1.set_title(f'Select the pair photo for the right side\n'
                      f'{first_photo_path}')
        # Add the subplot of small photos on the right
        candidate_index = 0
        sub_ax = []
        for r in range(0, 3):
            for c in range(3, 5):
                if candidate_index == len(candidates):
                    break
                sub_ax.append(fig.add_subplot(gs[r, c]))
                sub_ax[candidate_index].imshow(
                    Image.open(candidates[candidate_index]))
                sub_ax[candidate_index].set_title(
                    f'photo {candidate_index + 1}')
                candidate_index += 1
        if candidate_index < len(candidates):
            for r in range(3, 5):
                for c in range(0, 6):
                    if candidate_index == len(candidates):
                        break
                    sub_ax.append(fig.add_subplot(gs[r, c]))
                    sub_ax[candidate_index].imshow(
                        Image.open(candidates[candidate_index]))
                    sub_ax[candidate_index].set_title(
                        f'photo {candidate_index + 1}')
                    candidate_index += 1
        tmp_f_p = os.path.join(self.photos_folder, "tmp.png")
        plt.savefig(tmp_f_p, format='png')
        plt.close()
        return candidates, first_photo_path
    
    def move_paired_photo(self, first_photo_path, candidates, select_nr):
        paired_photo = candidates.pop(abs(select_nr) - 1)
        
        a_photo = first_photo_path if select_nr >= 0 else paired_photo
        b_photo = paired_photo if select_nr >= 0 else first_photo_path
        a_ending = a_photo.split('.')[-1]
        b_ending = b_photo.split('.')[-1]
        
        shutil.move(a_photo, os.path.join(
            self.train_a_path, f'{self.train_a_start_index}.{a_ending}'))
        self.train_a_start_index += 1
        
        shutil.move(b_photo, os.path.join(
            self.train_b_path, f'{self.train_b_start_index}.{b_ending}'))
        self.train_b_start_index += 1
        return candidates
    
    def run(self):
        
        photo_path, photo_list = self.pick_one_folder()
        continue_pair = True
        user_event = ''
        select_nr = None
        first_photo_as = None
        while photo_list is not None and continue_pair:
            
            if user_event == "To Other folder" or len(photo_list) < 2:
                self.skip_folder.append(photo_path)
                self.update_skip_folder_log()
                # pick up a new folder
                photo_path, photo_list = self.pick_one_folder()
                
            elif user_event == "Check folder":
                call(["open", photo_path])

            elif user_event == "Open all folders":
                for f in [self.train_a_path, self.train_b_path, photo_path]:
                    call(["open", f])
                
            candidates, first_photo_path = self.generate_bg_png(
                photo_list, first_photo_as)
            
            continue_pair, user_event, select_nr = user_do_pair(
                os.path.join(self.photos_folder, "tmp.png"))

            if user_event == 'First Photo as':
                first_photo_as = candidates[int(select_nr)-1]
                select_nr = None
            else:
                first_photo_as = None
                
            if select_nr is not None:
                photo_list = self.move_paired_photo(
                    first_photo_path, candidates, select_nr)
        
        if photo_list is None:
            tmp = os.path.join(self.photos_folder, "tmp.png")
            if os.path.exists(tmp):
                os.remove(tmp)
            finish_windows()
