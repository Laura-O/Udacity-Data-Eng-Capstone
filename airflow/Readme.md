# Certificats

The pipeline code requires the certificates of the API. They are included in the repository but might be outdated at some time.

To update them, download all certificates for a page in the browser and then run

    openssl x509 -in server.cer -inform DER -outform PEM  >> consolidate.pem