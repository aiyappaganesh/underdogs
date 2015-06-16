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

function updateProjectCategory() {
    var selectedCategory = $($('#category-select').parent('.selecter').find('.selected')[0]).attr('data-value');
    $('#category').val(selectedCategory);
    console.log();
}

$(document).ready(function(){
    updateProjectSkills();
});