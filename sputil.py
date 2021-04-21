#
# Copyright 2021 Sony Corporation
# SPDX-License-Identifier: MIT
#
"""
Utilities to handle Sharepoint API access.
"""
import os
import sys

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.client_context import ClientContext
from tqdm import tqdm

# import msal


class Sharepoint:
    """
    Class that handles access to Sharepoint.
    """

    _LOGIN_URL = "https://login.microsoftonline.com"
    _SCOPE = ".default"
    _MESSAGE = 2  # ClientRequestException.args[2] is error message

    def __init__(self, fconf, spconfig, runtime, logger):
        self._fconfig = fconf
        self._spconfig = spconfig
        self._runtime = runtime
        self._logger = logger
        self._context_auth = None
        self._url = None

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def get_token(self):
        """
        Acquire token for the site given the app client credentials.
        """

        ## Use MSAL:
        # authority_url = self._LOGIN_URL + f"/{self._tenant_id}"
        # app = msal.ConfidentialClientApplication(
        #     authority=authority_url,
        #     client_id=self._client_id,
        #     client_credential=self._client_secret,
        #     validate_authority=False,
        # )

        # token = app.acquire_token_for_client(
        #     scopes=[self._client_id + f"/{self._SCOPE}"]
        # )
        # if self._runtime.debug:
        #     self._logger.debug(token)
        # return token

        if self._spconfig.subsite:
            self._url = self._spconfig.site + "/" + self._spconfig.subsite
        else:
            self._url = self._spconfig.site

        if self._runtime.debug:
            self._logger.debug(self._url)

        self._context_auth = AuthenticationContext(url=self._url)
        self._context_auth.acquire_token_for_app(
            client_id=self._spconfig.client, client_secret=self._spconfig.secret
        )

    def verify_url(self):
        """
        Verify that the url given with runtime configuration actually
        exists on the Sharepoint site given in global configuration.
        Must authenticate using get_token first.
        """

        ctx = ClientContext(self._url, self._context_auth)
        try:
            web = ctx.web.get().execute_query()
        except ClientRequestException as err:
            self._logger.error(err.args[self._MESSAGE])
            return False

        self._logger.success(f"Site {web.properties['Title']}: {web.url}")
        return True

    def add_folder(self):
        """
        Add folder given in FilesConfig.out to the list collection of the Sharepoint
        site from the configuration.
        """

        ctx = ClientContext(self._url, self._context_auth)
        target_folder = ctx.web.lists.get_by_title("Documents").root_folder
        new_folder = target_folder.add(self._fconfig.out_folder)
        try:
            ctx.execute_query()
        except ClientRequestException as err:
            self._logger.error(err.args[self._MESSAGE])
            return False

        self._logger.success(f"Added folder: {new_folder.serverRelativeUrl}")
        return True

    def upload_files(self):
        """
        Upload files from configuration to the Sharepoint site from the configuration.
        """

        ctx = ClientContext(self._url, self._context_auth)
        root = ctx.web.lists.get_by_title("Documents").root_folder
        target_folder = root.folders.get_by_url(self._fconfig.out_folder)
        file_size = 0

        for f in self._fconfig.files:
            self._logger.info(f"File upload: {os.path.basename(f)}")
            file_size = os.path.getsize(f)

            with tqdm(
                total=file_size,
                file=sys.stdout,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                ascii=True,
            ) as pbar:

                def display_upload_progress(offset):  # pylint: disable=unused-argument
                    # print_progress callback in create_upload_session requires
                    # the offset parameter to show progress like:
                    #  (`offset` out of `file_size` uploaded)
                    # but tqdm instead works with `chunk_size`, i.e. size of step to
                    # update the progress bar.
                    """
                    Callback used to print progress to stdout during file update.
                    """

                    # pbar is only ever used here, so it's safe to silence
                    # the warning from pylint.
                    pbar.update(  # pylint: disable=cell-var-from-loop
                        self._runtime.chunk_size
                    )

                uploaded_file = target_folder.files.create_upload_session(
                    f, self._runtime.chunk_size, display_upload_progress
                )
                try:
                    ctx.execute_query()
                except ClientRequestException as err:
                    self._logger.error(err.args[self._MESSAGE])
                    return False

            self._logger.success(
                f"File {f} uploaded to: {uploaded_file.serverRelativeUrl}"
            )

        return True
