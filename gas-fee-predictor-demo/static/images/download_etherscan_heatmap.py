import requests
import os
import time

def download_etherscan_heatmap():
    # URL of the Etherscan heatmap
    url = "https://etherscan.io/images/gastracker/heatmap.png"
    
    # Add a timestamp to avoid caching
    url_with_timestamp = f"{url}?t={int(time.time())}"
    
    try:
        # Send a GET request to the URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url_with_timestamp, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Ensure the output directory exists
            output_dir = os.path.join(os.getcwd(), 'static', 'images')
            os.makedirs(output_dir, exist_ok=True)
            
            # Save the image
            output_path = os.path.join(output_dir, 'etherscan_heatmap.png')
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"Etherscan heatmap downloaded successfully to {output_path}")
            return True
        else:
            print(f"Failed to download Etherscan heatmap. Status code: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    download_etherscan_heatmap()
