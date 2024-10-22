# import-wp-to-framer
Convert the xml WordPress result to Framer csv (post to post)

SAB.ID move from WordPress self-host to Framer, which more easy to maintain and it's simple to use.<br>
On SAB.ID, we have more than 700 post and it's gonna take a lot of time if we move it manually.

And we don't see any plugin or tools that can convert a gutenberg post to framer rich-text editor, So, we build our own.<br>
with just a few change and click, you can also move your WordPress post to framer.

## Hire SAB.ID
If you don't want to mess with your WordPress, or just wanted to moving fast.<br>
You can [Hire Us](https://www.sab.id/), to help you perform WordPress migration to Framer [Hire Us](https://www.sab.id/).


## How to use this tools?

### Install Python and package
First, you need to ensure that you've already install python3 and install the package needed:
* xml.etree.ElementTree as ET
* csv
* logging
* re
* unescape
* os
* requests
* tqdm


### import the xml from WordPress
Import the post as usual from WordPress tools (Make sure that you already select the post).

### Change some of the code
The code intend only for our issue, but you can always change it to your needs.<br>
* See on Line 72, change the URL of example.com to your own domain, and ensure that you didn't block or rate-limit
* We use rank math as our plugin before, and for the post excerpt We copy it from rank_math_description, you can revert it to post_excerpt by removing the line of 57 - 61, and add the post excerpt by yourself
* See line 84 - 92, this is Our own framer fields, you can change it to your needed, and you also need to change the line of 164
* After all of above already complete, You need to define what file that need to be convert, see line 174.

### Convert it
After all above already installed, you just need to run `python3 wordpress-to-framer-converter.py`, you don't need to wory if it's running or not.<br>
We've already add visual progress in it, so you can see the progress:<br>
![image](https://github.com/user-attachments/assets/52303e02-947f-4f9a-8792-3f93bc0f6d25)
<br>
You should see the result similiar like this:<br>
![image](https://github.com/user-attachments/assets/97431499-c585-4c86-bbe8-51761126b970)<br>

### Upload it on Framer
And after all it's done, you can upload it to Framer


## Known Issue
Here a list of the issue you might encountered

### Why it's split to more than one .csv file?
We do this because Framer have a limitation upload size, so We must reduce the files, I limited to 5 MB file's below.

### Why some or one field is empty?
There's three possibilites.
* The data is empty
* Wrong calling data
* Wrong field name
