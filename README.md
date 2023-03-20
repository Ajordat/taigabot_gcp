# Taigabot GCP

This project aims to create a bot that allows for automation of creating User Stories programatically through the means of a Cloud Function triggered by Cloud Scheduler.

## 1. Installation

To have the bot up and running, it is needed to configure the resources and deploy the code into Cloud Functions.

### 1.1. Initial setup

1. Create an account in Taiga for your bot.
2. Set some environment variables so that the commands below can be used easily:
    ```bash
    export TAIGABOT_SA=taigabot-sa
    export TAIGABOT_ACCOUNT_SECRET_NAME=taigabot-account
    export TAIGABOT_PASSWORD_SECRET_NAME=taigabot-password

    export PROJECT_ID=$(gcloud config get core/project)
    export TAIGABOT_SA_FULL="${TAIGABOT_SA}@${PROJECT_ID}.iam.gserviceaccount.com"
    ```
    Feel free to modify the above values to fit your naming conventions, or leave those as a default value.
    
2. Create the Service Account (SA) that will be responsible of executing the whole workflow:
    ```bash
    gcloud iam service-accounts create ${TAIGABOT_SA} \
        --description="Service Account for the Taigabot account." \
        --display-name="Taigabot Service Account"
    ```
    As `${TAIGABOT_SA}` was used to name the SA it means that its associated email address will be `${TAIGABOT_SA}@${PROJECT_ID}.iam.gserviceaccount.com`. This full address was already anticipated and was stored in `${TAIGABOT_SA_FULL}` during the second step.
3. Upload the bot's credentials to Secret Manager. I present below two methods of uploading those values securely from the CLI:

    1. First method: reading from STDIN with `read` without echoing the pressed keys, using the value and clearing the environment variable.
        ```bash
        read -s TAIGABOT_ACCOUNT
        echo -n $TAIGABOT_ACCOUNT | gcloud secrets create ${TAIGABOT_ACCOUNT_SECRET_NAME} \
            --replication-policy="automatic" \
            --data-file=-
        export TAIGABOT_ACCOUNT=
        ```
        ```bash
        read -s TAIGABOT_PASSWORD
        echo -n $TAIGABOT_PASSWORD | gcloud secrets create ${TAIGABOT_PASSWORD_SECRET_NAME} \
            --replication-policy="automatic" \
            --data-file=-
        export TAIGABOT_PASSWORD=
        ```
    2. Second method: Write the value to a temporary file, use it to create the secret and delete the file.
        ```bash
        export tmpfile=$(mktemp)
        vim tmpfile
        gcloud secrets create ${TAIGABOT_ACCOUNT_SECRET_NAME} --replication-policy="automatic" \
            --data-file=tmpfile
        rm tmpfile
        ```
        ```bash
        export tmpfile=$(mktemp)
        vim tmpfile
        gcloud secrets create ${TAIGABOT_PASSWORD_SECRET_NAME} --replication-policy="automatic" \
            --data-file=tmpfile
        rm tmpfile
        ```
    

4. Grant the SA access to the created secrets:
    ```bash
    gcloud secrets add-iam-policy-binding ${TAIGABOT_ACCOUNT_SECRET_NAME} \
        --member="serviceAccount:${TAIGABOT_SA_FULL}" --role="roles/secretmanager.secretAccessor"

    gcloud secrets add-iam-policy-binding ${TAIGABOT_PASSWORD_SECRET_NAME} \
        --member="serviceAccount:${TAIGABOT_SA_FULL}" --role="roles/secretmanager.secretAccessor"
    ```

5. Optional. If you want to store the templates in Cloud Storage, create the bucket. Make sure to replace the values in `<>`. For the bucket I'd suggest to make it a regional bucket in the same region as the CF.

    ```bash
    export BUCKET_NAME=<BUCKET_NAME>
    gcloud storage buckets create gs://${BUCKET_NAME} \
        --default-storage-class=STANDARD \
        --location=<BUCKET_LOCATION> \
        --uniform-bucket-level-access
    ```

    And grant the Taigabot SA with read access to the bucket's objects.
    ```bash
    gcloud storage buckets add-iam-policy-binding gs://${BUCKET_NAME} \
        --member="serviceAccount:${TAIGABOT_SA_FULL}" --role=roles/storage.objectViewer
    ```

### 1.2. Deployment

Once the previous setup is done, deploy this repository to Cloud Functions. You could do this simply with:

```bash
git clone https://github.com/Ajordat/taigabot_gcp
cd taigabot_gcp
```

Make sure to modify the file "cloudbuild.yaml" so that the values in `substitutions` match your settings.

Lastly, trigger the build with the following command:
```bash
gcloud builds submit .
```


