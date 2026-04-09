import pandas as pd
import os
import requests
import time
import base64
import requests
import time
import cloudinary
import cloudinary.uploader

# --- CONFIGURATION ---
ACCESS_TOKEN = "EAAdDD4cKxacBRPCWWL5mYCz0aFWrA3N41ZBBFnXSZBa9sslFdPfHxyyzVXemwUAckiv19zWJYUul9ZAGwLSWZATI9ae5UFRHfCGH43OmOdGySgLOWYV4zZBhaEfNkK6ZCWr9cBxLqvZCVcMSF3j2cKZBPQZCyZAVuX2CP3d1FcvHrKluuyUeRc7tt4PbXhhxl70ZARK2eLqAU73" #os.getenv("INSTAGRAM_ACCESS_TOKEN")
IG_USER_ID = "17841480606710089"  #os.getenv("INSTAGRAM_ACCOUNT_ID")
IMGBB_API_KEY = "6d9801bd3d0f13b8a22111870c54201e"

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def upload_to_instagram(local_image_path, caption):
    try:
        # -------------------------------
        # STEP 1: Upload to Cloudinary
        # -------------------------------
        print(f"--- Step 1: Uploading {local_image_path} to Cloudinary ---")

        upload_result = cloudinary.uploader.upload(local_image_path)
        public_image_url = upload_result["secure_url"]

        print(f"Public Image URL: {public_image_url}")

        # -------------------------------
        # STEP 2: Create Media Container
        # -------------------------------
        print("--- Step 2: Creating Instagram Container ---")

        post_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"

        payload = {
            "image_url": public_image_url,
            "caption": caption,
            "access_token": ACCESS_TOKEN
        }

        response = requests.post(post_url, data=payload)
        result = response.json()

        if "id" not in result:
            print("❌ Error creating container:", result)
            return False

        creation_id = result["id"]
        print(f"Creation ID: {creation_id}")

        # -------------------------------
        # STEP 3: Poll Status (IMPORTANT)
        # -------------------------------
        print("--- Step 3: Waiting for processing ---")

        status_url = f"https://graph.facebook.com/v19.0/{creation_id}"
        params = {
            "fields": "status_code",
            "access_token": ACCESS_TOKEN
        }

        for _ in range(10):  # max ~50 seconds
            status_res = requests.get(status_url, params=params).json()
            status = status_res.get("status_code")

            print(f"Status: {status}")

            if status == "FINISHED":
                break

            elif status == "ERROR":
                print("❌ Media processing failed:", status_res)
                return False

            time.sleep(5)
        else:
            print("❌ Timeout waiting for media processing")
            return False

        # -------------------------------
        # STEP 4: Publish
        # -------------------------------
        print("--- Step 4: Publishing to Instagram ---")

        publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"

        publish_res = requests.post(publish_url, data={
            "creation_id": creation_id,
            "access_token": ACCESS_TOKEN
        }).json()

        if "id" in publish_res:
            print("✅ Success! Posted to Instagram.")
            return True
        else:
            print("❌ Publish failed:", publish_res)
            return False

    except Exception as e:
        print("❌ Unexpected error:", str(e))
        return False

def run_automation():
    # Load CSV
    df = pd.read_csv('quotes.csv')
    
    # Find first unposted quote
    try:
        index = df[df['Posted'] == False].index[0]
    except IndexError:
        print("All quotes have been posted!")
        return

    row = df.loc[index]
    sn = row['SN']
    
    # Path logic
    bg_image = f"image_post/image_post ({sn}).jpg"
    output_file = "final_post.jpg"
    
    if not os.path.exists(bg_image):
        print(f"Error: File {bg_image} not found.")
        return

    # Generate the Image (Importing from your other file)
    from instagram_post import create_proverb_post 
    create_proverb_post(
        image_path=bg_image,
        quote_text=row['Quote'],
        author_name=row['Author'],
        logo_path="profile.png",
        output_name=output_file
    )

    sn = row['SN']

    caption1 = """Not everyone is meant to understand your journey.
    Some are meant to watch you rise.

    Stay disciplined. Stay dangerous. ⚔️

    Follow for daily warrior mindset 🔥

    #motivation #mindset #discipline #selfgrowth #successmindset #warriormindset #mentalstrength #focus #grind #growthmindset #selfimprovement #dailyquotes #inspiration #hustle #stayhard #innerstrength #personaldevelopment #consistency #riseabove #noexcuses #mindsetshift #alpha #strength #quotesdaily #warrior"""

    caption2 = """You don’t need motivation.
    You need discipline when motivation disappears.

    That’s where warriors are built. ⚔️

    Follow for real mindset 🔥

    #disciplineequalsfreedom #mindsetmatters #motivationdaily #selfdiscipline #successquotes #warriorlife #growth #focusmode #mentality #hustlehard #inspirationalquotes #stayfocused #dreambig #workhard #strongmind #riseandgrind #selfbelief #powerwithin #dailyinspiration #keepgoing #nevergiveup #successdriven #grindmode #warriorethos"""

    caption3 = """Pain is temporary.
    Weakness is forever.

    Choose wisely. ⚔️

    Follow to become unstoppable 🔥

    #painandgain #mentaltoughness #warriorcode #strengthmindset #motivationquotes #discipline #noexcuses #stayhard #mindsetiseverything #selfgrowthjourney #inspire #focusonyourself #hardworkpaysoff #innerpower #determination #fearless #riseup #grinddaily #successmotivation #believeinyourself #pushyourlimits #warriorquotes #darkmotivation #stoic #alphamindset"""

    caption4 = """Every day you delay…
    someone else is becoming stronger than you.

    Act now. ⚔️

    Follow for daily discipline 🔥

    #motivation #discipline #selfgrowth #mindset #success #warrior #focus #growth #hustle #grind #mindsetshift #selfimprovement #dailyquotes #inspiration #consistency #noexcuses #riseabove #mentalstrength #stayhard #dreambig #workhard #believe #progress #strength #warriormindset"""
        
    # Upload and Update
    mod = sn % 4

    if mod == 1:
        caption = caption1
    elif mod == 2:
        caption = caption2
    elif mod == 3:
        caption = caption3
    else:
        caption = caption4
        
    if upload_to_instagram(output_file, caption):
        df.at[index, 'Posted'] = True
        df.to_csv('quotes.csv', index=False)
        print(f"CSV updated for Quote #{sn}")

if __name__ == "__main__":
    run_automation()
