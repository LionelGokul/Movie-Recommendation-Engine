$(document).ready(function(){
    $('.loader').hide();

     $("#zeromovies").dialog({
         autoOpen: false,
         position: 'relative',
         left: '50%'
     });

    $("#movies").on("keyup", function() {
    if(this.value.length > 3){
        $.ajax({
         type: "POST",
         contentType: "application/json; charset=utf-8",
         url: "/get-movies-list",
         data: JSON.stringify(this.value),
         datatype: "json",
         success: function (result) {
           //do something
           $('#movieslist')
                .find('option')
                .remove()
                .end()
            $.each(result, function( index, value ) {
              $('#movieslist').append($("<option></option>").attr("value", value).text(value));
            });
          },
         error: function (xmlhttprequest, textstatus, errorthrown) {
             alert(" conection to the server failed ");
             console.log("error: " + errorthrown);
         }
      });//end of $.ajax()
    }
    });

    $('.search_icon').click(function(){
        $.blockUI({
            message: $('.loader'),
            css: {border: 'none','background-color': 'transparent', color:'white', 'font-size':'100%' }
            });

        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: "/get-recommendations",
            data: JSON.stringify($('#movies').val()),
            datatype: "json",
            success: function (result) {
                $('.cards').remove()
                var html = "";
                var rowEnding = 0;
                var results = JSON.parse(result);
                var size = Object.keys(results).length;

                if(size == 0)
                {
                    alert("Movie Not Found");
                }
                else
                {
                    html += '<div class="cards">';
                    $.each(results, function( index, value ) {
                        html += '<div class=" card [ is-collapsed ] ">';

                        if(value.image_url === ""){
                        value.image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQng1gxF7cf47WLUvmL6QUT1ik1K35yY8D2osfVu16ugQelfMU&s";
                        }

                        html+= '<div class="card__inner [ js-expander ]"><div class="matchpercentage">'+Math.round(value.match)+'% match</div><img src="'+value.image_url +'" class="flip-image" alt="'+value.title+'"/></div>';
                        html+='<div class="card__expander"><div class="movie_card" id="ave"> <i class="fa fa-close [ js-collapser ]"></i><div class="info_section"> <div class="movie_header"> <h1>'+value.title +'</h1> <h4>'+value.release_date.substring(6,)+'          <span class="imdb">Imdb:'+value.rating+'</span></h4> <span class="minutes">'+value.runtime+' minutes</span> <p class="type">'+value.genres.split(" ")+'</p> </div> <div class="movie_desc"> <p class="text">'+value.plot+'</p> </div> </div> <div class="blur_back" style="background: url('+value.image_url+')" > </div> </div></div></div>';
                    });
                    html += '</div>';

                    $('.recommended-movies-container').append(html);
                }

               $.unblockUI();

               var $cell = $('.card');
                //open and close card when clicked on card
                $cell.find('.js-expander').click(function() {

                  var $thisCell = $(this).closest('.card');
                  if ($thisCell.hasClass('is-collapsed')) {
                    $cell.not($thisCell).removeClass('is-expanded').addClass('is-collapsed').addClass('is-inactive');
                    $thisCell.removeClass('is-collapsed').addClass('is-expanded');

                    if ($cell.not($thisCell).hasClass('is-inactive')) {
                      //do nothing
                    } else {
                      $cell.not($thisCell).addClass('is-inactive');
                    }

                  } else {
                    $thisCell.removeClass('is-expanded').addClass('is-collapsed');
                    $cell.not($thisCell).removeClass('is-inactive');
                  }
                });

                //close card when click on cross
                $cell.find('.js-collapser').click(function() {

                  var $thisCell = $(this).closest('.card');

                  $thisCell.removeClass('is-expanded').addClass('is-collapsed');
                  $cell.not($thisCell).removeClass('is-inactive');

                });
             },
            error: function (xmlhttprequest, textstatus, errorthrown) {
                alert("conection to the server failed");
                console.log("error: " + errorthrown);
                $.unblockUI();
            }
        });//end of $.ajax()
    });
});