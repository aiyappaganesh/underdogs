function updateProjectCategory() {
    var selectedCategory = $($('#category-select').parent('.selecter').find('.selected')[0]).attr('data-value');
    $('#category').val(selectedCategory);
}

$(document).ready(function(){
    updateProjectCategory();
});