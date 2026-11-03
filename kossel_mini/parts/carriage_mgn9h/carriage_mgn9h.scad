// Kossel Mini carriage for HIWIN MGN9H linear rail blocks.
// Derived from carriage.scad of jcrocholl/kossel (GPLv3). The ball joint
// horns (separation 40), the ball joint screw and the belt clamps are the
// original geometry, raised by the height difference between MGN12H and
// MGN9H so they keep the same distance from the tower face.
include <configuration.scad>;

separation = 40;
thickness = 6;

horn_thickness = 13;
horn_x = 8;

belt_width = 5;
belt_x = 5.6;
belt_z = 7;

body_width = 27;

mgn12h_height = 13;
mgn9h_height = 10;
lift = mgn12h_height - mgn9h_height;

mgn9h_hole_across = 15;
mgn9h_hole_along = 16;
block_center_y = -10.5;
tail_bottom_y = -24;

screw_head = "countersunk";
base_top = lift + thickness;
csk_head_radius = 3.1;
csk_depth = 1.6;
socket_seat = 5;
socket_head_radius = 3.0;

module original_solids() {
  translate([0, 4, thickness/2])
    cube([body_width, 40, thickness], center=true);
  for (x = [-1, 1]) {
    scale([x, 1, 1]) intersection() {
      translate([0, 15, horn_thickness/2])
        cube([separation, 18, horn_thickness], center=true);
      translate([horn_x, 16, horn_thickness/2]) rotate([0, 90, 0])
        cylinder(r1=14, r2=2.5, h=separation/2-horn_x);
    }
  }
  difference() {
    union() {
      translate([6.5, -2.5, horn_thickness/2+1])
        cube([14, 7, horn_thickness-2], center=true);
      translate([10.75, 2.5, horn_thickness/2+1])
        cube([5.5, 16, horn_thickness-2], center=true);
    }
    translate([20, -10, 12.5]) rotate([35, 35, 30])
      cube([40, 40, 20], center=true);
  }
  for (y = [-12, 7]) {
    translate([1.25, y, horn_thickness/2+1])
      cube([7, 8, horn_thickness-2], center=true);
  }
}

module original_joint_cuts() {
  translate([0, 16, horn_thickness/2]) rotate([0, 90, 0])
    cylinder(r=m3_wide_radius, h=60, center=true, $fn=12);
  for (x = [-1, 1]) {
    scale([x, 1, 1]) translate([horn_x, 16, horn_thickness/2])
      rotate([90, 0, -90])
        cylinder(r1=m3_nut_radius, r2=m3_nut_radius+0.5, h=8, center=true, $fn=6);
  }
}

module countersink(z) {
  translate([0, 0, z - csk_depth])
    cylinder(r1=m3_wide_radius, r2=csk_head_radius, h=csk_depth + 0.01, $fn=36);
  translate([0, 0, z]) cylinder(r=csk_head_radius, h=50, $fn=36);
}

module mgn9h_screws() {
  for (x = [-1, 1]) for (y = [-1, 1]) {
    translate([x * mgn9h_hole_across/2, block_center_y + y * mgn9h_hole_along/2, 0]) {
      translate([0, 0, -1]) cylinder(r=m3_wide_radius, h=50, $fn=24);
      if (screw_head == "countersunk")
        countersink(base_top);
      else
        translate([0, 0, socket_seat]) cylinder(r=socket_head_radius, h=50, $fn=36);
    }
  }
}

module carriage_mgn9h() {
  difference() {
    union() {
      translate([0, 0, lift]) original_solids();
      linear_extrude(height=lift + 0.01) projection(cut=true) original_solids();
      translate([-body_width/2, tail_bottom_y, 0])
        cube([body_width, -16 - tail_bottom_y + 1, lift + thickness]);
    }
    translate([0, 0, lift]) original_joint_cuts();
    mgn9h_screws();
  }
}

carriage_mgn9h();
