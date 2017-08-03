Shrinkmeister - an lazy, aws-lambda powered thumbnail application
=================================================================

This application provide lazy-thumbnail replacement for sorl-thumnail package and move generation task to amazon - lambda service.
With shrinkmeister you don't need to pre-generate thumbnails for large images (or large quanatity of images) during request-response cycle,
you can remove thumbnails for rare visiting pages to scale down your storage space.

Server part can work not only for django project, but for any client type.

How this works
--------------

- Actual thumbnail generation removed from request-response cycle and instead return encrypted url for lambda application.
- When (and only when) client browser request this image url lambda application starts, generates thumbnail and return redirect to this thumbnail for browser.
- After generation lambda application store information about generated thumbnail to cache shared with clients.
- Next time your application call for get_thubmnail it will get actual thumbnail url from the cache and will not trigger lambda.

Installtion
-----------

Server part
...........

First you need to run server part (which is actual thumbnail generator) as amazon lambda application:
- Application code contains `shrink_server` - ready to start django application
- To run django project on amazon lambda you need `zappa` pacakge. Install it to virtualenv and run `zappa init`. This projcet very well documented.
- Set this enviroment variables in `zappa_settings.json` for your enviroment:
  - THUMBNAIL_SECRET_KEY - secret key for client-server request encryption
  - THUMBNAIL_BUCKET - where to store your thumbnails
  - THUMBNAIL_CACHE_BACKEND (default - redis) - driver for shared cache between lambda-server and your client to store information about generated thumbnails
  - THUMBNAIL_CACHE_NAME - name for shared cache
  - THUMBNAIL_CACHE_LOCATION - location for shared cache
  - THUMBNAIL_CACHE_KEY_PREFIX - key prefix for shrinkmeister information
  - THUMBNAIL_TTL - how long thumbnails information will be stored in cache
  - ALLOWED_HOST - host for your application (you will get this after `zappa deploy` command)
- Run `zappa deploy` and fill `ALLOWD_HOST`
- Run `zappa update`

Client
......

- Add `shrinkmeister` in your project and fill **same settings** that you set for server.
- Fill THUMBNAIL_SERVER_URL for your server url.