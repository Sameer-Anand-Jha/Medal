import os
import glob
import numpy as np
import cv2

# Source and destination paths (use raw strings or double backslashes)
src = r'D:\Academics\Sem_2\EE_691_RnD_Project\Git\96171d81-6aab-4a58-bdf4-2de8fa3e48f3\WSI'
dest = r'D:\Academics\Sem_2\EE_691_RnD_Project\Git\patches_tum_ntum\destination'
mpath = r'D:\Academics\Sem_2\EE_691_RnD_Project\Git\patches_tum_ntum\mask_n'

# Parameters
window = 512
threshold = 210
slide = 1
tot_count = window * window

# List image files
fold = glob.glob(os.path.join(src, '*'))
print(f'Found {len(fold)} files.')

for f1 in fold:
    print(f'Processing file: {f1}')
    fname = os.path.basename(f1)
    dest_fname = os.path.splitext(fname)[0]

    # Derive folder name (safe fallback if no '__' in name)
    foldname = fname.split('__')[0] if '__' in fname else dest_fname

    # Create output directory
    output_folder = os.path.join(dest, foldname)
    os.makedirs(output_folder, exist_ok=True)
    os.chdir(output_folder)

    # Read input image and corresponding mask
    img = cv2.imread(f1)
    mask_path = os.path.join(mpath, fname)
    mask = cv2.imread(mask_path, 0)

    if img is None or mask is None:
        print(f"Skipping {fname} — image or mask missing.")
        continue

    row, col = img.shape[:2]
    
    for i in range(0, row, int(window / slide)):
        rfirst_index = i if i + window <= row else row - window
        rlast_index = rfirst_index + window

        for j in range(0, col, int(window / slide)):
            cfirst_index = j if j + window <= col else col - window
            clast_index = cfirst_index + window

            mask_patch = mask[rfirst_index:rlast_index, cfirst_index:clast_index]
            patch = img[rfirst_index:rlast_index, cfirst_index:clast_index]

            # Skip patches that are too small
            if patch.shape != (512, 512, 3):
                continue

            # Check black area in mask
            black_count = np.sum(mask_patch == 0)
            percent_black = black_count * 100 / tot_count

            if percent_black <= 40.0:
                # Check how white the patch is
                channel_1 = patch[:, :, 0] > threshold
                channel_2 = patch[:, :, 1] > threshold
                channel_3 = patch[:, :, 2] > threshold
                white_pixels = np.logical_and(np.logical_and(channel_1, channel_2), channel_3)
                white_ratio = np.count_nonzero(white_pixels) * 100 / tot_count

                if white_ratio < 40:
                    patch_filename = f"{dest_fname}_{i}_{j}.png"
                    cv2.imwrite(patch_filename, patch)
                    print(f"Saved patch: {patch_filename}")
