$(document).ready(function() {
    // console.log('page alert from home.js')
    //$('body').load('/party');
});

//$("#partyMemberForm").submit(function(){
$("#AddPartyMember").on("click", function(){
    //alert("handler for submit called");
    let charName = $("#characterNameInput").val();
    let tactLv = $("input[type=radio][name=tacticianOptions]:checked").val();
    let lvlHead = $("input[type=radio][name=levelHeadedOptions]:checked").val();
    let quick = $("input[type=radio][name=quickHesitantOptions][id=quickEdge]:checked").val() || 0;
    let hesitant = $("input[type=radio][name=quickHesitantOptions][id=hesitantHindrance]:checked").val() || 0;
    
    let sessionID = $("#partyMemberForm").attr('data-id');

    let json_party_member = {
        'name': charName,
        'tactician': parseInt(tactLv),
        'level_headed': parseInt(lvlHead),
        'quick': parseInt(quick),
        'hesitant': parseInt(hesitant)
    };

    $.ajax({
        type: 'POST',
        url: '/' + sessionID + '/party/add',
        data: JSON.stringify(json_party_member),
        dataType: 'json',
        contentType: 'application/json',
        success: function() {
            $('body').load('/party')
        },
        error: function(e) {
            alert('POST FAILED');
        }
    });

})

$("#startInitiative").on("click", function(){
    alert("starting initative...")
});

$(".edit-character-button").on('click', function() {
    let charname = $(this).attr('data-charname');
    $("#character-modal").attr('data-oldname', charname);
    charname = charname.replace(" ", "-").toLowerCase();
    let character = null;

    let sessionID = $('#party').attr('data-sessionid');

    $.ajax({
        type: 'GET',
        url: '/' + sessionID + '/party/' + charname,
        success: function(response){
            character = response;
            // console.log(character);
            $("#modal-charname-input").val(character.name);
            
            for(var i=0; i < 3; i++){
                let query = "#levelHeaded" + i.toString();
                let query2 = ".lvlheadlabel" + i.toString();
                if(i === character.level_headed){
                    $(query).prop('checked', true);
                    $(query2).addClass("active");
                } else {
                    $(query).prop('checked', false);
                    $(query2).removeClass("active");
                }
            }
            
            for(var j=0; j<3; j++){
                let query = "#tactician" + j.toString();
                let query2 = ".tactlabel" + j.toString();
                if(j === character.tactician){
                    $(query).prop('checked', true);
                    $(query2).addClass("active");
                } else {
                    $(query).prop('checked', false);
                    $(query2).removeClass("active");
                }
            }
           
            if(character.quick > 0){
                $("#quickEdge").prop('checked', true);
                $(".quicklabel").addClass("active");
                $("#hesitantHindrance").prop('checked', false);
                $(".hesitantlabel").removeClass("active");
                $("#noQuickHesitant").prop('checked', false);
                $(".nonelabel").removeClass("active");
            } else if (character.hesitant > 0) {
                $("#quickEdge").prop('checked', false);
                $(".quicklabel").removeClass("active");
                $("#hesitantHindrance").prop('checked', true);
                $(".hesitantlabel").addClass("active");
                $("#noQuickHesitant").prop('checked', false);
                $(".nonelabel").removeClass("active");
            } else {
                $("#quickEdge").prop('checked', false);
                $(".quicklabel").removeClass("active");
                $("#hesitantHindrance").prop('checked', false);
                $(".hesitantlabel").removeClass("active");
                $("#noQuickHesitant").prop('checked', true);
                $(".nonelabel").addClass("active");
            }
        },
        error: function(e){
            alert("Character Failed to Load");
        }
    });

    $("#character-modal").modal();
});

$("#submit-modal").on('click', function(){
    let oldName = $("#character-modal").attr("data-oldname");
    let charName = $("#modal-charname-input").val();
    let tactLv = $("input[type=radio][name=tacticianOptions]:checked").val() || 0;
    let lvlHead = $("input[type=radio][name=levelHeadedOptions]:checked").val() || 0;
    let quick = $("input[type=radio][name=otherOptions][id=quickEdge]:checked").val() || 0;
    let hesitant = $("input[type=radio][name=otherOptions][id=hesitantHindrance]:checked").val() || 0;
    
    let sessionID = $("#party").attr('data-sessionid');

    let json_party_member = {
        'name': charName,
        'tactician': parseInt(tactLv),
        'level_headed': parseInt(lvlHead),
        'quick': parseInt(quick),
        'hesitant': parseInt(hesitant)
    };
    console.log(json_party_member);

    $.ajax({
        type: 'POST',
        url: '/' + sessionID + '/party/' + oldName.replace(" ", "-").toLowerCase(),
        data: JSON.stringify(json_party_member),
        dataType: 'json',
        contentType: 'application/json',
        success: function() {
            $('body').load('/party');
        },
        error: function(e) {
            alert('POST FAILED');
        }

    });

});
