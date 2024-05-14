//这个页面是默认的布局页面，包含了meta信息，以及页面的布局，
//这个页面是所有页面的父组件，所有的页面都是在这个页面的基础上进行开发的。
// layouts
import Container from "layouts/container";

type Meta = {
  title?: string | null;
  description?: string | null;
  image?: string | null;
  url?: string | null;
};

type Props = {
  meta?: Meta;
  children: React.ReactNode;
  noPadding?: boolean;
  bg?: "primary" | "secondary";
  noHeader?: boolean;
  breadcrumbs?: JSX.Element;
  left?: JSX.Element;
  right?: JSX.Element;
};

const DefaultLayout: React.FC<Props> = ({ meta, children }) => (
  <Container meta={meta}>
    <div className="w-full h-screen overflow-auto bg-gray-50">
      <>{children}</>
    </div>
  </Container>
);

export default DefaultLayout;
