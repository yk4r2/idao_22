echo "Downloading data"
git clone https://github.com/HSE-LAMBDA/IDAO-2022.git
echo "Unzipping files"
tar -xf IDAO-2022/data/dichalcogenides_private.tar.gz
tar -xf IDAO-2022/data/dichalcogenides_public.tar.gz
echo "Cleaning the things up"
rm -r IDAO-2022
echo "All set!"

