var axis_map = [];
var domain_map = [];
var xScale, yScale, radiusScale, colorScale;

function render(){
  init_axis_map();
  render_chart($('#skill_selector').val());
}

function init_axis_map(){
  $("#axis_selectors select").each(function(index){
    axis_map[$(this).attr("id")] = $(this).val().toLowerCase();
  });
}

function reload(){
  $.get( "/temp/company_data?skill=" + $('#skill_selector').val(), function(data) {
      update_chart( JSON.parse(data) );
    })
    .fail(function() {
      alert( "error" );
    });
}

function re_render(){
  init_axis_map();
  init_scales();
  init_axes();
  init_axis_labels();
  init_skill_label();
  reload();
}

function update_chart(startups){
  company_data = startups['companies'];
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

function x(d) { return d[axis_map['x_axis']]; }
function y(d) { return d[axis_map['y_axis']]; }
function radius(d) { return d[axis_map['radius']]; }
function color(d) { return d.name; }
function key(d) { return d.name; }

var margin = {top: 19.5, right: 19.5, bottom: 19.5, left: 39.5},
      width = 960 - margin.right,
      height = 400 - margin.top - margin.bottom;

function init_scales(){
  xScale = d3.scale.linear().domain(domain_map[axis_map['x_axis']]).range([0, width]);
  yScale = d3.scale.linear().domain(domain_map[axis_map['y_axis']]).range([height, 0]);
  radiusScale = d3.scale.sqrt().domain(domain_map[axis_map['radius']]).range([0, 20]);
  colorScale = d3.scale.category10();
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

  d3.json("/temp/company_data?skill=" + sel_skill, function(error, startups) {
    if(error) return console.warn(error);
    var bisect = d3.bisector(function(d) { return d[0]; });
    domain_map = startups['domain'];
    init_scales();
    init_axes();
    init_axis_labels();
    init_skill_label();

    var dot = svg.append("g")
        .attr("class", "dots")
      .selectAll(".dot")
        .data(startups['companies'])
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
  });
}