function updateProjectSkills() {
    var skills = '';
    $('#skills-select').parent('.selecter').find('.selected').each(function(){
        var val = $(this).attr('data-value');
        if(skills != '') {
            skills = skills + ',';
        }
        skills = skills + val;
    });
    $('#project-skills').val(skills);
}

$(document).ready(function(){
    updateProjectSkills();
});