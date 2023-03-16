import SimpleITK as sitk
import pandas as pd
import numpy as np
import shutil
import os
import time
import itk

# Filters
exp                = sitk.ExpImageFilter()                         # Exponential Filter
MinMax_filter      = sitk.MinimumMaximumImageFilter()              # Minimun Maximum Filter
SignedDanielssonDM = sitk.SignedDanielssonDistanceMapImageFilter() # DanielssonDistance Filter
SignedDanielssonDM.SetUseImageSpacing(True)

def dm_computation(out_OARs, out_path, i, file=False):
    
    obtain_dm_img(out_OARs, out_path, i)

def obtain_dm_img(out_OARs, file_dm_final, i):
    
    # Segmentation
    # Label Map -> Each voxel is associated to a specific structure:
    #    - 0: Background
    #    - 1: Rectum
    #    - 2: Bladder
    #    - 3: Prostate
    #    - 4: Seminal vesicles
    # Prostate--------------------------------------------------------------------------------------------------------------
    prostate = (out_OARs==3)
    # Bladder---------------------------------------------------------------------------------------------------------------
    bladder  = (out_OARs==2)
    # Prostate+Bladder------------------------------------------------------------------------------------------------------
    prost_blad = prostate+bladder
    
    #----------------------------------------------------------------------------------------------------------------------#
    # Distance Map computation
    #----------------------------------------------------------------------------------------------------------------------#
    start_case = time.time()
    
    #---------- Segmentation Prostate ----------#
    # Signed Danielsson DM: computes a signed distance map with the approximation to the euclidean distance.
    prostate_SignedDanielssonDM   = SignedDanielssonDM.Execute(sitk.Cast(prostate, sitk.sitkUInt8))
    prostate_in = (prostate_SignedDanielssonDM*sitk.Cast((prostate==1)*(1), sitk.sitkFloat32))*(-1)
    MinMax_filter.Execute(prostate_in);
    max_value   = MinMax_filter.GetMaximum();
    prostate_in = (max_value - prostate_in)*sitk.Cast((prostate==1)*(1), sitk.sitkFloat32)
    
    #---------- Segmentation Bladder ----------#
    # Signed Danielsson DM: computes a signed distance map with the approximation to the euclidean distance.
    bladder_SignedDanielssonDM   = SignedDanielssonDM.Execute(sitk.Cast(bladder, sitk.sitkUInt8))
    bladder_in = (bladder_SignedDanielssonDM*sitk.Cast((bladder==1)*(1), sitk.sitkFloat32))*(-1)
    MinMax_filter.Execute(bladder_in);
    max_value = MinMax_filter.GetMaximum();
    bladder_in = (max_value - bladder_in)*sitk.Cast((bladder==1)*(1), sitk.sitkFloat32)
    bladder_in_weighted = (bladder_in/prostate_SignedDanielssonDM)
    
    #---------- Segmentation Prostate+Bladder ----------#
    # Signed Danielsson DM: computes a signed distance map with the approximation to the euclidean distance.
    prostate_bladder_SignedDanielssonDM   = SignedDanielssonDM.Execute(sitk.Cast(prost_blad, sitk.sitkUInt8))
    euclidean_out = (prostate_bladder_SignedDanielssonDM*sitk.Cast((prost_blad!=1)*(1), sitk.sitkFloat32))*(-1)

    dm_in    = prostate_in + sitk.Cast(bladder_in_weighted,sitk.sitkFloat32)
    dm_final = dm_in + euclidean_out
    print("--- Processing DM total : %s seconds ---" % (time.time() - start_case))
    
    sitk.WriteImage(dm_final, file_dm_final, True)
    print('Saving... '+ file_dm_final)
    
    

    
    
  