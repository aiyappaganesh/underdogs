var axis_map = [];
var domain_map = [];
var skills_heirarchy = [];
var global_startups = null;
var xScale, yScale, radiusScale, colorScale;

$(document).ready(function(){
    $('.axis-parameter').change(function(){
        init_axis_map();
        initialize();
        update_chart();
    });
    $('.expertise-parameter').change(function(){
        update_chart();
    });
});

function render(){
  pull_skills_heirarchy();
}

function pull_skills_heirarchy(){
  $.get( "/temp/skills_heirarchy", function(data) {
      skills_heirarchy = JSON.parse(data);
      render_skills_selector();
      init_axis_map();
      render_chart($('#skill_selector').val());
    })
    .fail(function() {
      alert( "error" );
    });
}

function add_skills_to(select, depth, key){
  depth_skills = skills_heirarchy[depth][key];
  if(depth > 0)
    select.append(new Option("--Optional--", ""));
  for (var i = 0; i < depth_skills.length; i++){
    if(depth < 2)
      select.append(new Option(depth_skills[i][1], depth_skills[i][0]));
    else
      select.append(new Option(depth_skills[i][0], depth_skills[i][0]));
  }
}

function render_skills_selector(){
  $('#skill_depth_1').show();
  var first_sel = $('#skill_depth_1 select');
  add_skills_to(first_sel, 0, 'skills');
  update_skills_selector(first_sel[0]);
}

function empty_selector(selector){
  selector.find('option').remove();
}

function hide_all_selectors_after(depth){
  for(var i = depth + 1; i <= 3; i++){
    empty_selector($('#skill_depth_' + i + ' select'));
    $('#skill_depth_' + i).css("display", "none");
  }
}

function update_skills_selector(sel){
  var skill_depth = parseInt(sel.name);
  if (skill_depth < 3) {
    var curr_sel = $('#skill_depth_' + skill_depth + ' select');
    var currentSelector = '#skill_depth_' + skill_depth + ' select';
    var childSelector = '#skill_depth_' + (skill_depth + 1);
    $(childSelector).show();
    $($(childSelector+' p')[0]).html($($(currentSelector+' option:selected')[0]).text()+' specialization');
    empty_selector($(childSelector + ' select'));
    add_skills_to($(childSelector + ' select'), skill_depth, curr_sel.val());
    hide_all_selectors_after(skill_depth + 1);
  };
}

function init_axis_map(){
  $("#axis_selectors select").each(function(index){
    axis_map[$(this).attr("id")] = $(this).val().toLowerCase();
  });
}

function init_axes(){
  var xAxis = d3.svg.axis().orient("bottom").scale(xScale).ticks(12, d3.format(",d")),
      yAxis = d3.svg.axis().scale(yScale).orient("left");
  d3.select(".x.axis").call(xAxis);
  d3.select(".y.axis").call(yAxis);
}

function init_axis_labels(){
  d3.select(".x.label").text(axis_map['x_axis']);
  d3.select(".y.label").text(axis_map['y_axis']);
}

function init_skill_label(){
  d3.select(".skill.label").text($('#skill_selector').val());
}

function init_scales(){
  xScale = d3.scale.linear().domain(domain_map[axis_map['x_axis']]).range([0, width]);
  yScale = d3.scale.linear().domain(domain_map[axis_map['y_axis']]).range([height, 0]);
  radiusScale = d3.scale.sqrt().domain(domain_map[axis_map['radius']]).range([0, 20]);
  colorScale = d3.scale.category10();
}

function initialize(){
  init_scales();
  init_axes();
  init_axis_labels();
  init_skill_label();
}

function re_render(){
  init_axis_map();
  initialize();
  update_chart();
}

function loadData() {
    if(!global_startups) {
        $.get( "/temp/company_data", function(data) {
            global_startups = JSON.parse(data);
        })
        .fail(function() {
            alert( "error" );
        });
    }
}

function update_chart(){
  loadData();
  company_data = global_startups['companies'];
  var company_map = {};
  for (var i = 0; i < company_data.length; i++) {
    company_map[company_data[i].id] = [xScale(x(company_data[i])), yScale(y(company_data[i]))];
  }

  d3.selectAll('circle')
    .transition()
    .duration(500)
    .attr("cx", function(d) {
      return company_map[d.id][0];
    })
    .attr("cy", function(d) {
      return company_map[d.id][1];
    });
    init_skill_label();
}

function get_expertise_sel(){
  var max_depth = 3;
  var skills_sel = [];
  for(var i = 1; i <= max_depth; i++){
    if($('#skill_depth_' + i).css('display') != "none"){
      var val = $('#skill_depth_' + i + ' select').val();
      if(val != "")
        skills_sel.push(val);
    }
  }
  return skills_sel;
}

function find_matching_child(key, children){
  for(var i = 0; i < children.length; i++){
    if(children[i]['key'] == key)
      return children[i];
  }
}

function get_expertise_val_for(d){
  var skills_sel = get_expertise_sel();
  curr_map = d['expertise'];
  curr_score = 0.0;
  for(var i = 0; i < skills_sel.length; i++){
    curr_children = curr_map['children'];
    child = find_matching_child(skills_sel[i], curr_children);
    curr_score = child['score'];
    curr_map = child;
  }
  return curr_score;
}

function get_float_val(d, key){
  data_lookup_key = axis_map[key];
  if(data_lookup_key == 'expertise')
    return get_expertise_val_for(d);
  else
    return d[data_lookup_key];
}

function x(d) { return get_float_val(d, 'x_axis'); }
function y(d) { return get_float_val(d, 'y_axis'); }
function radius(d) { return get_float_val(d, 'radius'); }
function color(d) { return d.name; }
function key(d) { return d.name; }

var margin = {top: 19.5, right: 19.5, bottom: 19.5, left: 39.5},
      width = 960 - margin.right,
      height = 400 - margin.top - margin.bottom;

function render_chart(sel_skill){
    var svg = d3.select("#chart").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")");

    svg.append("g")
      .attr("class", "y axis");

    svg.append("text")
      .attr("class", "x label")
      .attr("text-anchor", "end")
      .attr("x", width)
      .attr("y", height - 6);

    svg.append("text")
      .attr("class", "y label")
      .attr("text-anchor", "end")
      .attr("y", 6)
      .attr("dy", ".75em")
      .attr("transform", "rotate(-90)");

    var label = svg.append("text")
      .attr("class", "skill label")
      .attr("text-anchor", "end")
      .attr("y", height - 24)
      .attr("x", width);

    if(!global_startups) {
        $.get( "/temp/company_data", function(data) {
            global_startups = JSON.parse(data);
            var bisect = d3.bisector(function(d) { return d[0]; });
            domain_map = global_startups['domain'];
            initialize();

            var dot = svg.append("g")
                .attr("class", "dots")
              .selectAll(".dot")
                .data(global_startups['companies'])
              .enter().append("circle")
                .attr("class", "dot")
                .attr("id", function(d){return d.id})
                .style("fill", function(d) { return colorScale(color(d)); })
                .call(position)
                .sort(order);

            dot.append("title")
                .text(function(d) { return d.name; });

            var box = label.node().getBBox();

            var overlay = svg.append("rect")
                  .attr("class", "overlay")
                  .attr("x", box.x)
                  .attr("y", box.y)
                  .attr("width", box.width)
                  .attr("height", box.height);

            function position(dot) {
              dot .attr("cx", function(d) { return xScale(x(d)); })
                  .attr("cy", function(d) { return yScale(y(d)); })
                  .attr("r", function(d) { return radiusScale(radius(d)); });
            }

            function order(a, b) {
              return radius(b) - radius(a);
            }
        })
        .fail(function() {
            alert( "error" );
        });
    }
}