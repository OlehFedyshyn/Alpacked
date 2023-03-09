const AWS = require('aws-sdk');
const AdmZip = require("adm-zip");
const s3 = new AWS.S3();
const fs = require('fs');
const mime = require('mime-types')
const watermark = require('jimp-watermark');

const base_path = '/tmp';
const images_folder = 'images';
const processed_images_folder = 'watermark';
const watermark_file_name = process.env.WATERMARK_FILE_NAME;
const allowed_mime_types = ['image/jpeg']

async function downloadS3Object(bucket, object_key, destination_path) {
    let readStream = s3.getObject({
        Bucket: bucket,
        Key: object_key
    }).createReadStream();

    return new Promise(resolve => {
        let writeStream = fs.createWriteStream(destination_path);
        readStream.pipe(writeStream);

        writeStream.on('finish', resolve);

        console.log(`Downloaded ${object_key} to ${destination_path}`);
    });
}

async function uploadS3Object(source_path, bucket, object_key) {
    const fileContent = fs.readFileSync(source_path);

    const params = {
        Bucket: bucket,
        Key: object_key,
        Body: fileContent
    };

    try {
        await s3.upload(params, function(err, data) {
            if (err) {
                throw err;
            }
        }).promise();
        console.log(`File uploaded successfully.`);
    } catch(e) {
        console.log(`Something went wrong. ${e}`);
    }
}

async function extractArchive(source_path, destination_path) {
    try {
        const zip = new AdmZip(source_path);
        const outputDir = destination_path;
        zip.extractAllTo(outputDir);

        console.log(`Extracted to "${outputDir}"`);
    } catch (e) {
        console.log(`Something went wrong. ${e}`);
    }
}

async function createArchive(source_path, destination_path) {
    try {
        const zip = new AdmZip();
        const outputFile = destination_path;
        zip.addLocalFolder(source_path);
        zip.writeZip(outputFile);
        console.log(`Created ${outputFile}`);
    } catch (e) {
        console.log(`Something went wrong. ${e}`);
    }
}


module.exports.handler = (async (event, context) => {
    console.log("EVENT: \n" + JSON.stringify(event, null, 2))

    const record = event['Records'][0]

    const bucket = record['s3']['bucket']['name']
    const object_key = record['s3']['object']['key']
    console.log(`Archive was uploaded to bucket ${bucket} with key ${object_key}`)
    // Downloading archive from S3 bucket
    await downloadS3Object(bucket, object_key, `${base_path}/${object_key}`)
    // Extracting files for archive
    await extractArchive(`${base_path}/${object_key}`, `${base_path}/${images_folder}`)
    // Creating list of images that was unpacked from archive
    let file_list = []
    fs.readdirSync(`${base_path}/${images_folder}`).forEach(file => {
        try {
            if (fs.lstatSync(`${base_path}/${images_folder}/${file}`).isFile()) {
                let type = mime.lookup(`${base_path}/${images_folder}/${file}`)
                if (allowed_mime_types.includes(type)) {
                    file_list.push(file);
                } else {
                    throw new Error('Wrong MIMEType!');
                }
            } else {
                throw new Error('Not a file!');
            }
        } catch (e) {
            return;
        }
    });
    if (!fs.existsSync(`${base_path}/${images_folder}/${processed_images_folder}`)){
        fs.mkdirSync(`${base_path}/${images_folder}/${processed_images_folder}`);
    }
    await downloadS3Object(bucket, watermark_file_name, `${base_path}/${watermark_file_name}`)
    file_list.forEach(file => {
        const options = {
            'dstPath' : `${base_path}/${images_folder}/${processed_images_folder}/${file}`
        };
        watermark.addWatermark(`${base_path}/${images_folder}/${file}`, `${base_path}/${watermark_file_name}`, options);
        let processed_image = file_list.pop();
        console.log(`Added watermark to image with filename: ${processed_image}`);
    })
    await createArchive(`${base_path}/${images_folder}/${processed_images_folder}`, `${base_path}/output.zip`)
    await uploadS3Object(`${base_path}/output.zip`, bucket, 'output.zip')
});