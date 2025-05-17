# Every Tree in Munich

Bayerische Vermessungsverwaltung makes complete tree data (probably done by deep learning on aerial imagery) from the whole Bayern
available as [open-data](https://geodaten.bayern.de/opengeodata/OpenDataDetail.html?pn=einzelbaeume).

Munich area is covered by the dataset [124029_baeume.gpkg](https://geodaten.bayern.de/odd/m/8/baeume3d/data/124028_baeume.gpkg).

~~~
curl -O https://geodaten.bayern.de/odd/m/8/baeume3d/data/124028_baeume.gpkg
~~~

There are 4,095,860 trees in the whole dataset `124029_baeume.gpkg` which contains 26 layers covering different areas.

Every layer cotains a collection of trees and every tree data entry has three important attributes:

 - `geom`: tree location coordinate
 - `dgmhoehe`: terrain elevation from digital terrain model (dt. digitales Geländemodell)
 - `baumhoehe`: tree height

We can use [ogrinfo](https://gdal.org/en/stable/programs/ogrinfo.html) to verify them:

~~~
> ogrinfo 124028_baeume.gpkg

> ogrinfo 124028_baeume.gpkg 5347_trees -so

> ogrinfo 124028_baeume.gpkg |
          grep -E '^\d+: ' |
          awk -F ': ' '{print $2}' |
          awk '{print $1}' |
          while read layer; do
            ogrinfo 124028_baeume.gpkg "$layer" -so |
            grep "Feature Count" |
            awk '{s+=$3} END {print s}';
          done |
          awk '{s+=$1} END {print s}'
~~~

We can extract trees only from Munich districts with [ogr2ogr](https://gdal.org/en/stable/programs/ogr2ogr.html):

~~~
> ogr2ogr -f GPKG munich_trees.gpkg 124028_baeume.gpkg \
          -clipsrc contrib/munich.boundary.geojson
~~~

Btw, there are 1,041,150 tress in the dataset for the whole Munich area.

Then, we generate GeoJSON files with map projection in EPSG:4326 for further tile processing.

~~~
> mkdir tmp_geojson

> for layer in $(ogrinfo munich_trees.gpkg | grep -E '^\d+: ' | awk -F ': ' '{print $2}' | awk '{print $1}'); do
    echo "Processing layer $layer..."
    ogr2ogr \
      -f GeoJSONSeq \
      -t_srs EPSG:4326 \
      tmp_geojson/${layer}.geojson \
      munich_trees.gpkg \
      $layer
    if [ ! -s tmp_geojson/${layer}.geojson ]; then
        rm tmp_geojson/${layer}.geojson
    fi
  done
~~~

Next, we use [tippecanoe](https://github.com/mapbox/tippecanoe/blob/master/README.md) to generate vector tiles in mbtiles format.
We will keep all tree data in the high map zoom levels and reduce clutter in the low zoom levels.
Finally, we merge all mbtiles files with `tile-join` and convert them to `pbf` format in ZXY folder convention with [mb-util](https://github.com/mapbox/mbutil)

~~~
> tippecanoe -o munich_trees_z17.mbtiles \
             --layer=trees --projection=EPSG:4326 \
             --minimum-zoom=17 --maximum-zoom=19 \
             --base-zoom=17 \
             --no-feature-limit --no-tile-size-limit \
             --buffer=64 --read-parallel \
             tmp_geojson/*.geojson

> tippecanoe -o munich_trees_z0z16.mbtiles \
             --layer=trees --projection=EPSG:4326 \
             --minimum-zoom=0 --maximum-zoom=16 \
             --drop-densest-as-needed \
             --maximum-tile-features=1000 \
             --drop-rate=1.5 \
             --buffer=24 --read-parallel \
             tmp_geojson/*.geojson

> tile-join -o munich_trees.mbtiles munich_trees_z0z16.mbtiles munich_trees_z17.mbtiles

> mb-util munich_trees.mbtiles --silent --image_format=pbf  tiles
~~~

To view the result locally `http://localhost:8000/` after running a local web server defined in `contrib/server.py`.

~~~
> python3 python3 contrib/server.py
~~~

To upload result for static file hosting (e.g., on Github) you may need to uncompress pbf files to workaround HTTP Content-Type. (Note: you can run local server with `-X` to serve uncompressed pbf.)

~~~
> find tiles -name '*.pbf' -print0 | xargs -0 -I{} sh -c '
    gzip -d -c "{}" > "{}.tmp" && mv "{}.tmp" "{}"
  '

> python3 python3 contrib/server.py -X
~~~

