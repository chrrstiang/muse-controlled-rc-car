"""
Quick analysis of recorded EEG data.

This script:
- Loads EEG data from CSV files
- Prints basic statistics (samples, duration, channels)
- Plots raw EEG data for first 4 seconds
- Calculates alpha/beta and theta/beta ratios for 2-second windows
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import argparse
import os
from signal_processing import calculate_band_power, plot_raw_eeg

def load_eeg_data(filename):
    """Load EEG data from CSV file."""
    if not os.path.exists(f'data/recordings/training/training_001/{filename}'):
        print(f"Error: File {filename} not found!")
        return None
    
    df = pd.read_csv(f'data/recordings/training/training_001/{filename}')
    return df

def print_basic_stats(df, sampling_rate=256):
    """Print basic statistics about the EEG data."""
    print("\n=== Basic Statistics ===")
    print(f"Number of samples: {len(df)}")
    print(f"Duration: {len(df)/sampling_rate:.2f} seconds")
    print(f"Channels: {list(df.columns[1:])}")  # Skip timestamp column
    print(f"Sampling rate: {sampling_rate} Hz")

def analyze_entire_file(df, channel='AF7', window_duration=2, sampling_rate=256):
    """Analyze entire file with sliding 2-second windows."""
    print(f"\n=== Entire File Analysis ===")
    print(f"Channel: {channel}")
    print(f"Window duration: {window_duration}s")
    
    total_samples = len(df)
    window_samples = int(window_duration * sampling_rate)
    num_windows = total_samples // window_samples
    
    print(f"Total samples: {total_samples}")
    print(f"Window samples: {window_samples}")
    print(f"Number of windows: {num_windows}")
    
    # Arrays to store results
    theta_powers = []
    alpha_powers = []
    beta_powers = []
    alpha_beta_ratios = []
    theta_beta_ratios = []
    
    # Analyze each window
    for i in range(num_windows):
        start_sample = i * window_samples
        end_sample = (i + 1) * window_samples
        
        # Extract window data
        window_data = df[channel].iloc[start_sample:end_sample].values
        
        # Calculate band powers
        theta_power = calculate_band_power(window_data, sampling_rate, 'theta')
        alpha_power = calculate_band_power(window_data, sampling_rate, 'alpha')
        beta_power = calculate_band_power(window_data, sampling_rate, 'beta')
        
        # Calculate ratios
        alpha_beta_ratio = alpha_power / beta_power
        theta_beta_ratio = theta_power / beta_power
        
        # Store results
        theta_powers.append(theta_power)
        alpha_powers.append(alpha_power)
        beta_powers.append(beta_power)
        alpha_beta_ratios.append(alpha_beta_ratio)
        theta_beta_ratios.append(theta_beta_ratio)
    
    # Calculate statistics
    print(f"\n=== Statistics ===")
    
    # Theta power statistics
    theta_mean = np.mean(theta_powers)
    theta_std = np.std(theta_powers)
    print(f"Theta Power - Mean: {theta_mean:.6f}, Std: {theta_std:.6f}")
    
    # Alpha power statistics
    alpha_mean = np.mean(alpha_powers)
    alpha_std = np.std(alpha_powers)
    print(f"Alpha Power - Mean: {alpha_mean:.6f}, Std: {alpha_std:.6f}")
    
    # Beta power statistics
    beta_mean = np.mean(beta_powers)
    beta_std = np.std(beta_powers)
    print(f"Beta Power - Mean: {beta_mean:.6f}, Std: {beta_std:.6f}")
    
    # Alpha/Beta ratio statistics
    alpha_beta_mean = np.mean(alpha_beta_ratios)
    alpha_beta_std = np.std(alpha_beta_ratios)
    print(f"Alpha/Beta Ratio - Mean: {alpha_beta_mean:.3f}, Std: {alpha_beta_std:.3f}")
    
    # Theta/Beta ratio statistics
    theta_beta_mean = np.mean(theta_beta_ratios)
    theta_beta_std = np.std(theta_beta_ratios)
    print(f"Theta/Beta Ratio - Mean: {theta_beta_mean:.3f}, Std: {theta_beta_std:.3f}")
    
    # Print arrays
    print(f"\n=== Raw Arrays ===")
    print(f"Theta Powers: {[f'{p:.6f}' for p in theta_powers]}")
    print(f"Alpha Powers: {[f'{p:.6f}' for p in alpha_powers]}")
    print(f"Beta Powers: {[f'{p:.6f}' for p in beta_powers]}")
    print(f"Alpha/Beta Ratios: {[f'{r:.3f}' for r in alpha_beta_ratios]}")
    print(f"Theta/Beta Ratios: {[f'{r:.3f}' for r in theta_beta_ratios]}")
    
    return {
        'theta_powers': theta_powers,
        'alpha_powers': alpha_powers,
        'beta_powers': beta_powers,
        'alpha_beta_ratios': alpha_beta_ratios,
        'theta_beta_ratios': theta_beta_ratios,
        'statistics': {
            'theta_mean': theta_mean, 'theta_std': theta_std,
            'alpha_mean': alpha_mean, 'alpha_std': alpha_std,
            'beta_mean': beta_mean, 'beta_std': beta_std,
            'alpha_beta_mean': alpha_beta_mean, 'alpha_beta_std': alpha_beta_std,
            'theta_beta_mean': theta_beta_mean, 'theta_beta_std': theta_beta_std
        }
    }

def main():
    parser = argparse.ArgumentParser(description='Quick analysis of EEG data')
    parser.add_argument('filename', help='EEG CSV file to analyze')
    parser.add_argument('--channel', default='AF7', help='Channel to analyze (default: AF7)')
    parser.add_argument('--sampling_rate', type=int, default=256, help='Sampling rate in Hz (default: 256)')
    
    args = parser.parse_args()
    
    # Load data
    df = load_eeg_data(args.filename)
    if df is None:
        return
    
    # Print basic statistics
    print_basic_stats(df, args.sampling_rate)
    
    # Analyze entire file with 2-second windows
    analyze_entire_file(df, channel=args.channel, sampling_rate=args.sampling_rate)
    
    # Plot raw EEG data
    plot_raw_eeg(df, channel=args.channel, sampling_rate=args.sampling_rate)

if __name__ == "__main__":
    main()