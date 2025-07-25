#pragma description Stormworks map data format

struct XYZ{
    float X;
    float Y_ZERO;
    float Z;
};


struct Single_Mesh{
    u16 num_positions;
    XYZ positions[num_positions];
    u16 num_edges;
    u16 edges[num_edges];
};

struct LineSegment{
    float from_X;
    float from_Y_ZERO;
    float from_Z;
    float a;
    float oneorzero;
};

struct LineStuff{
    u16 length;
    LineSegment segments[length];    
};

struct MapData{
    Single_Mesh meshes[11];
    LineStuff ls[10];
};

MapData map@0x00;