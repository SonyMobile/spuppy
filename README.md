# spuppy
SharePoint UPload in PYthon is a collection of scripts used to work with
SharePoint instance provided in configuration. For now, you can only
upload files to the Documents area of a SharePoint site.

They use SharePoint's REST-like API to achieve their goals.

## Set up

### Dependencies
* To use run: `pip install -r requirements.txt`
* To develop:
  - run: `pip install -r dev-requirements.txt`
    This will install packages required for development and git pre-commit
    hook.
  - execute: `pre-commit install`
    This will install pre-commit hook in your git to run the dev tools
    on commit.

### Configuration
Update configuration in `config.yaml` with appropriate SharePoint IDs and URLs.

```
sp:
  tenant: "tenant-id-of-the-sharepoint-site"
  client: "client-id-of-the-sharepoint-app-used-to-access-sharepoint-api"
  site: "url/to/the/sharepoint/site/handled/by/client"
  secret: "client-secret-used-to-authenticate-with-the-sharepoint-app"
runtime:
  debug: True|False # get additional debug printouts
  chunk_size: n # bytes
```

### How to?
In order to be able to access SharePoint APIs a SharePoint app has to be
used on the SharePoint site.

Follow:
```
https://site_url/_layouts/15/appregnew.aspx
```
to create and register the SharePoint app and its authentication key.

To grant the necessary permissions to the app, go to:
```
https:///site_url/_layouts/15/appinv.aspx
```
lookup your app by its client-id and paste in the permission xml,
that looks something like:
```xml
<AppPermissionRequests AllowAppOnlyPolicy="true">
    <AppPermissionRequest Scope="http://sharepoint/content/sitecollection"
        Right="FullControl" />
</AppPermissionRequests>
```

Note: This is only an example permission xml. Find the permissions here:
https://docs.microsoft.com/en-us/sharepoint/dev/sp-add-ins/add-in-permissions-in-sharepoint#available-scopes-and-permissions-and-restrictions-on-office-store-apps-permissions


## Run

### spup.py
Upload a file to a specified folder of a Sharepoint site.

Usage:
```
spup.py [-h] [-d] [-s SUBSITE] [-i DIRECTORY] [-f FILES] [-o OUT]

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           print additional debug information
  -s SUBSITE, --subsite SUBSITE
                        subsite of a configured Sharepoint site
  -i DIRECTORY, --directory DIRECTORY
                        folder with files to upload (if no files specified,
                        upload the whole directory)
  -f FILES, --files FILES
                        comma separated list of files to upload (if not
                        specified, upload the -i directory)
  -o OUT, --out OUT     folder name to create at the target site (if not
                        specified, use the folder name of -i directory
```

## Contributing
Submit an issue or create a Merge Request.
If it's your first code contribution, please add your name to [AUTHORS](AUTHORS) file in alphabetical order.

## LICENSE
Copyright 2021 Sony Corporation
The project is licensed under the MIT license.
See [LICENSE](LICENSE) file.

