var m = [20, 120, 20, 120],
    w = 1000 - m[1] - m[3],
    h = 600 - m[0] - m[2],
    i = 0,
    root;

var tree = d3.layout.tree()
    .size([h, w]);

var diagonal = d3.svg.diagonal()
    .projection(function(d) { return [d.y, d.x]; });

var vis = null;

function addGraph(){
  vis = d3.select("#body").append("svg:svg")
    .attr("width", w + m[1] + m[3])
    .attr("height", h + m[0] + m[2])
    .append("svg:g")
    .attr("transform", "translate(" + m[3] + "," + m[0] + ")");
}

function toggleAll(d) {
  if (d.children) {
    d.children.forEach(toggleAll);
    toggle(d);
  }
}

function reload(){
  d3.select("svg").remove();
  var company_id = $('#companies select').val();
  populateMembers(company_id);
  render('company_id=' + company_id);
}

function populateMembers(company_id){
  $.get( "/temp/company_members?company_id=" + company_id, function(data) {
    members = JSON.parse(data);
    var select = $('#members select');
    select.find('option').remove();
    select.append(new Option('--Optional--', ''));
    for(var i = 0; i < members.length; i++){
      select.append(new Option(members[i].name, members[i].id));
    }
  })
  .fail(function() {
    alert( "error" );
  });
}

function loadMemberData(){
  d3.select("svg").remove();
  var member_id = $('#members select').val();
  var company_id = $('#companies select').val();
  render('member_id=' + member_id + '&company_id=' + company_id);
}

function render(query){
  addGraph();
  d3.json("/temp/skills_data?" + query, function(error, root) {
    if (error) return console.warn(error);
    root.x0 = h / 2;
    root.y0 = 0;
    toggleAll(root);
    update(root, root);
  });
}

function update(root, source) {
  var duration = d3.event && d3.event.altKey ? 5000 : 500;
  var nodes = tree.nodes(root).reverse();
  nodes.forEach(function(d) { d.y = d.depth * 180; });
  var node = vis.selectAll("g.node")
      .data(nodes, function(d) { return d.id || (d.id = ++i); });
  var nodeEnter = node.enter().append("svg:g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
      .on("click", function(d) { toggle(d); update(root, d); });
  nodeEnter.append("svg:circle")
      .attr("r", 1e-6)
      .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });
  nodeEnter.append("svg:text")
      .attr("x", function(d) { return d.children || d._children ? -10 : 10; })
      .attr("dy", ".35em")
      .attr("text-anchor", function(d) { return d.children || d._children ? "end" : "start"; })
      .text(function(d) { var name = d.name; if(d.score){name = name + " : " + d.score}; return name; })
      .style("fill-opacity", 1e-6);
  var nodeUpdate = node.transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });
  nodeUpdate.select("circle")
      .attr("r", 4.5)
      .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });
  nodeUpdate.select("text")
      .style("fill-opacity", 1);
  var nodeExit = node.exit().transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
      .remove();
  nodeExit.select("circle")
      .attr("r", 1e-6);
  nodeExit.select("text")
      .style("fill-opacity", 1e-6);
  var link = vis.selectAll("path.link")
      .data(tree.links(nodes), function(d) { return d.target.id; });
  link.enter().insert("svg:path", "g")
      .attr("class", "link")
      .attr("d", function(d) {
        var o = {x: source.x0, y: source.y0};
        return diagonal({source: o, target: o});
      })
    .transition()
      .duration(duration)
      .attr("d", diagonal);
  link.transition()
      .duration(duration)
      .attr("d", diagonal);
  link.exit().transition()
      .duration(duration)
      .attr("d", function(d) {
        var o = {x: source.x, y: source.y};
        return diagonal({source: o, target: o});
      })
      .remove();
  nodes.forEach(function(d) {
    d.x0 = d.x;
    d.y0 = d.y;
  });
}

function toggle(d) {
  if (d.children) {
    d._children = d.children;
    d.children = null;
  } else {
    d.children = d._children;
    d._children = null;
  }
}

function updateMember() {
    var select = $('#members select');
    select.empty();
    name = $('#companies select option:selected').attr('name');
    id = $('#companies select option:selected').attr('id');
    select.append(new Option(name, id));
    loadMemberData();
}