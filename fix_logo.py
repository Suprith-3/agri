import shutil
import os
import glob

def fix_logo():
    # The directory where the AI saves the images you upload
    brain_dir = r'C:\Users\supre\.gemini\antigravity\brain\0d6079e3-68dc-425f-96c6-8a6e08dfed8e'
    
    # Look for the logo image (the one with the tree)
    # We look for files starting with 'media__' and pick the most recent one
    files = glob.glob(os.path.join(brain_dir, 'media__*'))
    
    if not files:
        print("❌ Could not find the logo image in the temporary folder.")
        return

    # Find the most recently uploaded image
    latest_file = max(files, key=os.path.getmtime)
    
    target_path = os.path.join('static', 'logo.png')
    
    try:
        # Create static folder if it doesn't exist
        if not os.path.exists('static'):
            os.makedirs('static')
            
        shutil.copy2(latest_file, target_path)
        print(f"✅ SUCCESS! Logo has been moved to: {target_path}")
        print("🚀 Refresh your browser now to see the new logo!")
    except Exception as e:
        print(f"❌ Error moving logo: {e}")

if __name__ == "__main__":
    fix_logo()
