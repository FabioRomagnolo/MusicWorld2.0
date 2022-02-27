/* Javascript for favorite tracks management
*
*  Requirements: JQuery 3.5.1
*  */

function favorites(favorite_tracks_ids, baseTrackURL) {
    var favorite_tracks_elems = document.querySelectorAll('[id^="i-fav-"]');

    for (const el of favorite_tracks_elems) {
        const track_id = el.id.split('-')[2];
        const icon_id = "i-fav-" + track_id;
        const btn_id = "btn-fav-" + track_id;

        // Checking if track is a favorite one
        if (favorite_tracks_ids.indexOf(track_id) >= 0) {
            $("#" + btn_id).empty().append("<i id=" + "\"" + icon_id + "\" class='star fas fa-star'></i>");
            $("#" + icon_id).attr('onClick', 'favoriteFunction(this, true, '+baseTrackURL+')');
        } else {
            $("#" + btn_id).empty().append("<i id=" + "\"" + icon_id + "\" class='star far fa-star'></i>");
            $("#" + icon_id).attr('onClick', 'favoriteFunction(this, false, '+baseTrackURL+')');
        }
    }
}

function favoriteFunction(el, favorite, baseTrackURL) {
    const track_id = el.id.split('-')[2];
    const icon_id = "i-fav-" + track_id;
    const btn_id = "btn-fav-" + track_id;

    const track_url = baseTrackURL + track_id;

    // Refreshing the favorites icon with loading icon
    $("#" + btn_id).empty().append("<i id=" + "\"" + icon_id + "\" class='star fas fa-spinner fa-spin'></i>");

    if (favorite === false) {
        // Adding track to favorites in the Firestore DB
        console.log("Sending POST request to "+track_url);
        $.ajax({
            type: "POST",
            //url: "{{url_for('track', track_id=null)}}" + track_id,
            url: track_url,
            success: function (response) {
                console.log('POST request successfully sent to ' + this.url);
                favorite = true;
                // Refreshing the favorites icon
                $("#" + btn_id).empty().append("<i id=" + "\"" + icon_id + "\" class='star fas fa-star'></i>");
                $("#" + icon_id).attr('onClick', 'favoriteFunction(this, true, '+baseTrackURL+')');
            },
            error: function (err) {
                console.log(err);
            }
        });
    } else {
        // Removing track from favorites in the Firestore DB
        console.log("Sending DELETE request to "+track_url)
        $.ajax({
            type: "DELETE",
            url: track_url,
            success: function (response) {
                console.log('DELETE request successfully sent to ' + this.url);
                favorite = false;
                // Refreshing the favorites icon
                $("#" + btn_id).empty().append("<i id=" + "\"" + icon_id + "\" class='star far fa-star'></i>");
                $("#" + icon_id).attr('onClick', 'favoriteFunction(this, false, '+baseTrackURL+')');
            },
            error: function (err) {
                console.log(err);
            }
        });
    }
}
